"""
CrisisInbox Environment Implementation.

An MCP environment simulating a 48-hour post-disaster inbox where an agent
must triage and respond to messages across multiple channels.

Features:
- Timeline engine: messages arrive at scheduled times as the clock advances
- Dependency chains: some actions require prerequisites to be completed first
- Schema drift: policies/deadlines change mid-episode (3 of 5 events per episode)
- Cognitive overload: more messages than can be optimally handled
"""

import json
import random
from typing import Any, Optional
from uuid import uuid4

from openenv.core.env_server.mcp_environment import MCPEnvironment
from openenv.core.env_server.types import Action, Observation, State
from fastmcp import FastMCP

try:
    from ..models import Channel, Message, Urgency
    from ..messages import ALL_MESSAGES
    from ..drift_events import ALL_DRIFT_EVENTS, DriftEvent, select_drift_events
except ImportError:
    from models import Channel, Message, Urgency
    from messages import ALL_MESSAGES
    from drift_events import ALL_DRIFT_EVENTS, DriftEvent, select_drift_events


class CrisisInboxEnvironment(MCPEnvironment):
    """
    Simulates a 48-hour post-disaster inbox triage scenario.

    The agent receives messages from family, employers, government agencies,
    insurance companies, and service providers. It must prioritize safety,
    meet deadlines, and adapt to changing rules (schema drift).

    Timeline engine:
    - Messages arrive at their scheduled timestamp_hours
    - Each action advances time by 0.25 hours (15 minutes)
    - Reading a message advances time by 0.1 hours (6 minutes)
    - Deadlines tick down as time passes
    - 3 random drift events fire at their trigger times

    MCP tools:
    - get_inbox: View messages that have arrived so far
    - read_message: Read a specific message in full
    - respond_to_message: Respond to / take action on a message
    - get_status: See current time, score, and handled messages
    - advance_time: Skip forward in time (in hours)
    """

    def __init__(self):
        mcp = FastMCP("crisis_inbox")

        # Environment state (set on reset)
        self._all_messages: list[Message] = []
        self._visible_messages: list[Message] = []
        self._handled: dict[str, str] = {}   # msg_id -> response
        self._read_msgs: set[str] = set()    # msg_ids that have been read
        self._current_hour: float = 0.0
        self._score: float = 0.0
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._drift_events: list[DriftEvent] = []
        self._fired_drifts: set[str] = set()
        self._superseded: dict[str, str] = {}  # old_msg_id -> new_msg_id
        self._rng = random.Random()

        @mcp.tool
        def get_inbox() -> str:
            """
            View all messages currently in the inbox.
            Returns a JSON list of message summaries (id, sender, subject, urgency,
            channel, timestamp, deadline, handled status, drift_flag).
            Only shows messages that have arrived by the current time.
            """
            self._deliver_messages()
            summaries = []
            for msg in self._visible_messages:
                is_superseded = msg.id in self._superseded
                summaries.append({
                    "id": msg.id,
                    "sender": msg.sender,
                    "subject": msg.subject,
                    "urgency": msg.urgency.value,
                    "channel": msg.channel.value,
                    "timestamp_hours": msg.timestamp_hours,
                    "deadline_hours": msg.deadline_hours,
                    "handled": msg.id in self._handled,
                    "read": msg.id in self._read_msgs,
                    "drift_flag": msg.drift_flag,
                    "superseded": is_superseded,
                })
            return json.dumps(summaries, indent=2)

        @mcp.tool
        def read_message(message_id: str) -> str:
            """
            Read the full content of a specific message.
            Costs 0.1 hours (6 minutes) of time.

            Args:
                message_id: The ID of the message to read (e.g. 'msg_001')

            Returns:
                Full message details as JSON, or error if not found.
            """
            self._deliver_messages()
            for msg in self._visible_messages:
                if msg.id == message_id:
                    self._read_msgs.add(message_id)
                    self._advance_clock(0.1)
                    result = msg.model_dump()
                    result["current_hour"] = self._current_hour
                    if msg.id in self._superseded:
                        result["WARNING"] = (
                            f"This message has been superseded by {self._superseded[msg.id]}. "
                            "Information may be outdated."
                        )
                    return json.dumps(result, indent=2)
            return json.dumps({"error": f"Message '{message_id}' not found or hasn't arrived yet"})

        @mcp.tool
        def respond_to_message(message_id: str, response: str) -> str:
            """
            Respond to or take action on a message. Costs 0.25 hours (15 minutes).

            Args:
                message_id: The ID of the message to respond to
                response: Your response or action description

            Returns:
                Result of the action including any reward earned.
            """
            self._deliver_messages()

            msg = None
            for m in self._visible_messages:
                if m.id == message_id:
                    msg = m
                    break

            if msg is None:
                return json.dumps({"error": f"Message '{message_id}' not found or hasn't arrived yet"})

            if message_id in self._handled:
                return json.dumps({"error": f"Message '{message_id}' already handled"})

            # Check dependencies
            unmet = [dep for dep in msg.dependencies if dep not in self._handled]
            if unmet:
                return json.dumps({
                    "error": f"Unmet dependencies: {unmet}. Handle those messages first."
                })

            # Calculate reward
            reward = _calculate_reward(
                msg, self._current_hour, response, self._superseded,
            )
            self._handled[message_id] = response
            self._score += reward

            # Advance time
            self._advance_clock(0.25)

            done = self._current_hour >= 48.0

            return json.dumps({
                "status": "handled",
                "message_id": message_id,
                "reward": reward,
                "total_score": self._score,
                "current_hour": self._current_hour,
                "messages_handled": len(self._handled),
                "messages_visible": len(self._visible_messages),
                "done": done,
            })

        @mcp.tool
        def get_status() -> str:
            """
            Get current environment status: time elapsed, score, progress,
            and active drift events.
            """
            self._deliver_messages()
            expired = []
            upcoming_deadlines = []
            for msg in self._visible_messages:
                if msg.id not in self._handled and msg.deadline_hours is not None:
                    if self._current_hour > msg.deadline_hours:
                        expired.append({"id": msg.id, "subject": msg.subject})
                    elif msg.deadline_hours - self._current_hour < 4.0:
                        upcoming_deadlines.append({
                            "id": msg.id,
                            "subject": msg.subject,
                            "hours_remaining": round(msg.deadline_hours - self._current_hour, 1),
                        })

            return json.dumps({
                "current_hour": self._current_hour,
                "total_score": self._score,
                "messages_total_arrived": len(self._visible_messages),
                "messages_handled": len(self._handled),
                "messages_remaining": len(self._visible_messages) - len(self._handled),
                "expired_deadlines": expired,
                "upcoming_deadlines": upcoming_deadlines,
                "drift_events_fired": len(self._fired_drifts),
                "done": self._current_hour >= 48.0,
            })

        @mcp.tool
        def advance_time(hours: float) -> str:
            """
            Advance the clock forward by the specified number of hours.
            New messages may arrive and deadlines may expire.

            Args:
                hours: Number of hours to advance (0.5 to 4.0)

            Returns:
                Status update with new messages and any expired deadlines.
            """
            hours = max(0.5, min(4.0, hours))
            old_visible_count = len(self._visible_messages)
            self._advance_clock(hours)
            new_visible_count = len(self._visible_messages)

            return json.dumps({
                "advanced_by": hours,
                "current_hour": self._current_hour,
                "new_messages": new_visible_count - old_visible_count,
                "total_visible": new_visible_count,
                "done": self._current_hour >= 48.0,
            })

        super().__init__(mcp)

    def _advance_clock(self, hours: float):
        """Advance the clock and deliver any new messages/drift events."""
        self._current_hour = min(48.0, self._current_hour + hours)
        self._deliver_messages()
        self._fire_drift_events()

    def _deliver_messages(self):
        """Make messages visible if their timestamp has been reached."""
        for msg in self._all_messages:
            if msg.timestamp_hours <= self._current_hour:
                if not any(m.id == msg.id for m in self._visible_messages):
                    self._visible_messages.append(msg)

    def _fire_drift_events(self):
        """Fire any drift events whose trigger time has been reached."""
        for drift in self._drift_events:
            if drift.id in self._fired_drifts:
                continue
            if self._current_hour >= drift.trigger_hour:
                self._fired_drifts.add(drift.id)
                # Add drift messages to the message pool
                for msg in drift.messages:
                    if not any(m.id == msg.id for m in self._all_messages):
                        self._all_messages.append(msg)
                # Track superseded messages
                for old_id in drift.superseded_msg_ids:
                    for dmsg in drift.messages:
                        if dmsg.supersedes == old_id:
                            self._superseded[old_id] = dmsg.id

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Observation:
        self._rng = random.Random(seed)

        # Build the message pool: start with non-drift messages
        drift_msg_ids = set()
        self._drift_events = select_drift_events(count=3, rng=self._rng)
        for drift in self._drift_events:
            for msg in drift.messages:
                drift_msg_ids.add(msg.id)

        # Filter ALL_MESSAGES: exclude drift messages that won't fire this episode
        all_drift_ids = set()
        for drift in ALL_DRIFT_EVENTS:
            for msg in drift.messages:
                all_drift_ids.add(msg.id)

        self._all_messages = []
        for msg in ALL_MESSAGES:
            if msg.id in all_drift_ids and msg.id not in drift_msg_ids:
                continue  # Skip drift messages from events not selected this episode
            m = msg.model_copy()
            # Add jitter to arrival times and deadlines for episode variation
            # Keep hour-0 messages at 0, jitter others by +/- 15% (clamped to 0-48)
            if m.timestamp_hours > 0:
                jitter = self._rng.uniform(-0.15, 0.15) * m.timestamp_hours
                m.timestamp_hours = max(0.1, min(47.5, m.timestamp_hours + jitter))
            if m.deadline_hours is not None and m.deadline_hours > 0:
                d_jitter = self._rng.uniform(-0.1, 0.1) * m.deadline_hours
                m.deadline_hours = max(
                    m.timestamp_hours + 0.5,
                    min(72.0, m.deadline_hours + d_jitter),
                )
            self._all_messages.append(m)

        self._visible_messages = []
        self._handled = {}
        self._read_msgs = set()
        self._current_hour = 0.0
        self._score = 0.0
        self._fired_drifts = set()
        self._superseded = {}

        self._state = State(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
        )

        # Deliver any messages at time 0
        self._deliver_messages()

        return Observation(
            done=False,
            reward=0.0,
            metadata={
                "status": "ready",
                "message": (
                    "Crisis inbox loaded. You have 48 hours to triage incoming messages. "
                    "Messages will arrive over time. Policies and deadlines may change."
                ),
                "messages_visible": len(self._visible_messages),
                "messages_total": len(self._all_messages),
                "drift_events_scheduled": len(self._drift_events),
                "scenario": "Post-hurricane evacuation and recovery in Sacramento",
            },
        )

    def _step_impl(
        self,
        action: Action,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> Observation:
        return Observation(
            done=False,
            reward=0.0,
            metadata={
                "error": f"Unknown action type: {type(action).__name__}. "
                "Use ListToolsAction or CallToolAction for MCP interactions."
            },
        )

    def step(
        self,
        action: Action,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> Observation:
        self._state.step_count += 1
        return super().step(action, timeout_s=timeout_s, **kwargs)

    @property
    def state(self) -> State:
        return self._state


def _calculate_reward(
    msg: Message,
    current_hour: float,
    response: str,
    superseded: dict[str, str],
) -> float:
    """
    Calculate reward for handling a message.

    Reward signals:
    - Base reward by urgency (critical=10, high=5, medium=3, low=1)
    - Deadline timing bonus (up to +50% for early, -75% for late)
    - Response quality (penalty for very short responses)
    - Schema drift adaptation bonus (+50% for handling drift messages)
    - Penalty for acting on superseded/stale information (-50%)
    """
    base_rewards = {
        Urgency.CRITICAL: 10.0,
        Urgency.HIGH: 5.0,
        Urgency.MEDIUM: 3.0,
        Urgency.LOW: 1.0,
    }
    reward = base_rewards.get(msg.urgency, 1.0)

    # Deadline timing
    if msg.deadline_hours is not None:
        if current_hour <= msg.deadline_hours:
            time_remaining_frac = (msg.deadline_hours - current_hour) / max(msg.deadline_hours, 1.0)
            reward *= 1.0 + 0.5 * time_remaining_frac
        else:
            reward *= 0.25

    # Response quality - penalty for very short/empty responses
    if len(response.strip()) < 10:
        reward *= 0.5

    # Drift adaptation bonus
    if msg.drift_flag:
        reward *= 1.5

    # Penalty for responding to a superseded message (stale info)
    if msg.id in superseded:
        reward *= 0.5

    return round(reward, 2)
