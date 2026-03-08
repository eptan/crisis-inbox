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
import re
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import Action, Observation, State

try:
    from ..models import Channel, Message, Urgency
    from ..messages import ALL_MESSAGES
    from ..drift_events import ALL_DRIFT_EVENTS, DriftEvent, select_drift_events
except ImportError:
    from models import Channel, Message, Urgency
    from messages import ALL_MESSAGES
    from drift_events import ALL_DRIFT_EVENTS, DriftEvent, select_drift_events


# ---------------------------------------------------------------------------
# Reward functions (inlined — single source of truth for server + notebooks)
# ---------------------------------------------------------------------------

_FAMILY_SENDERS = {"mom", "sister", "neighbor dave", "emma"}
_FAMILY_TONE_WORDS = {"love", "safe", "worried", "sorry", "care", "okay", "miss", "hang in there"}
_FORMAL_TONE_WORDS = {"confirm", "attached", "documentation", "regarding", "request", "please", "submit"}


def tone_multiplier(sender: str, response: str) -> float:
    """Small reward multiplier for tone-appropriate responses (1.0-1.15)."""
    resp_lower = response.lower()
    sender_lower = sender.lower()
    if any(f in sender_lower for f in _FAMILY_SENDERS):
        matches = sum(1 for w in _FAMILY_TONE_WORDS if w in resp_lower)
        if matches >= 2:
            return 1.15
        elif matches == 1:
            return 1.07
    else:
        matches = sum(1 for w in _FORMAL_TONE_WORDS if w in resp_lower)
        if matches >= 2:
            return 1.1
        elif matches == 1:
            return 1.05
    return 1.0


def calculate_reward(
    msg: Message,
    current_hour: float,
    response: str,
    superseded: dict[str, str],
    visible_messages: list[Message] | None = None,
    handled: dict[str, str] | None = None,
) -> float:
    """Calculate triage reward for handling a message.

    Components: urgency base (1-10), deadline timing, response quality,
    tone matching, drift bonus (+50%), stale penalty (-50%),
    conflict bonus (+25%), priority penalty (-70%).
    """
    base_rewards = {
        Urgency.CRITICAL: 10.0,
        Urgency.HIGH: 5.0,
        Urgency.MEDIUM: 3.0,
        Urgency.LOW: 1.0,
    }
    reward = base_rewards.get(msg.urgency, 1.0)

    if msg.deadline_hours is not None:
        if current_hour <= msg.deadline_hours:
            time_remaining_frac = (msg.deadline_hours - current_hour) / max(msg.deadline_hours, 1.0)
            reward *= 1.0 + 0.5 * time_remaining_frac
        else:
            reward *= 0.25

    if len(response.strip()) < 10:
        reward *= 0.5

    reward *= tone_multiplier(msg.sender, response)

    if msg.drift_flag:
        reward *= 1.5

    if msg.id in superseded:
        reward *= 0.5

    if msg.conflicts_with:
        reward *= 1.25

    if visible_messages and handled is not None:
        has_unhandled_critical = any(
            m.urgency == Urgency.CRITICAL and m.id not in handled
            for m in visible_messages
            if m.id != msg.id
        )
        if has_unhandled_critical and msg.urgency in (Urgency.LOW, Urgency.MEDIUM):
            reward *= 0.3

    return round(reward, 2)


def score_format(completion: str) -> float:
    """Format compliance reward (0.0 to 2.0). Bootstraps GRPO learning."""
    score = 0.0
    if "respond_to_message" in completion:
        score += 0.5
    if re.search(r'msg_\d+', completion):
        score += 0.5
    if re.search(r'respond_to_message\s*\(', completion):
        score += 0.5
    if re.search(r'respond_to_message\s*\(\s*["\']?msg_\d+["\']?\s*,\s*["\']', completion):
        score += 0.5
    return score


def score_action(completion: str, prompt_data: dict) -> float:
    """Score a model completion: format reward (0-2) + triage reward.

    This is the single source of truth — notebooks inline this same logic.
    """
    messages = prompt_data["messages"]
    hour = prompt_data["hour"]
    superseded = prompt_data.get("superseded", {})

    fmt_reward = score_format(completion)

    match = re.search(
        r'respond_to_message\s*\(\s*["\']?(msg_\d+)["\']?\s*,\s*["\'](.+?)["\']',
        completion, re.DOTALL,
    )
    if match:
        msg_id = match.group(1)
        response_text = match.group(2)
    else:
        id_match = re.search(r'(msg_\d+)', completion)
        if id_match:
            msg_id = id_match.group(1)
            response_text = completion
        else:
            return fmt_reward

    target_dict = next((m for m in messages if m["id"] == msg_id), None)
    if target_dict is None:
        return fmt_reward + 0.5

    target_msg = Message(
        id=target_dict["id"],
        sender=target_dict["sender"],
        channel=target_dict.get("channel", "email"),
        subject=target_dict.get("subject", ""),
        content=target_dict.get("content", ""),
        urgency=target_dict["urgency"],
        timestamp_hours=target_dict.get("timestamp_hours", 0.0),
        deadline_hours=target_dict.get("deadline_hours"),
        dependencies=target_dict.get("dependencies", []),
        drift_flag=target_dict.get("drift_flag", False),
        supersedes=target_dict.get("supersedes"),
    )

    handled_ids = {m["id"]: "" for m in messages if m.get("handled", False)}
    visible = [
        Message(
            id=m["id"],
            sender=m["sender"],
            channel=m.get("channel", "email"),
            subject=m.get("subject", ""),
            content=m.get("content", ""),
            urgency=m["urgency"],
            timestamp_hours=m.get("timestamp_hours", 0.0),
            deadline_hours=m.get("deadline_hours"),
            dependencies=m.get("dependencies", []),
            drift_flag=m.get("drift_flag", False),
            supersedes=m.get("supersedes"),
        )
        for m in messages
    ]

    triage_reward = calculate_reward(
        msg=target_msg,
        current_hour=hour,
        response=response_text,
        superseded=superseded,
        visible_messages=visible,
        handled=handled_ids,
    )

    return round(fmt_reward + triage_reward, 2)


# ---------------------------------------------------------------------------
# OpenEnv Action / Observation models (pure HTTP, no MCP)
# ---------------------------------------------------------------------------

class CrisisInboxAction(Action):
    """Action for the CrisisInbox environment.

    tool_name selects the operation; arguments carries its parameters.
    """
    tool_name: str = Field(
        default="get_inbox",
        description="Tool: get_inbox, read_message, respond_to_message, get_status, get_prompt, advance_time, score_batch",
    )
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description='Tool arguments as JSON (e.g. {"message_id": "msg_001", "response": "On my way"})',
    )


class CrisisInboxObservation(Observation):
    """Observation returned by every step."""
    result: dict[str, Any] | list[dict[str, Any]] | str = Field(
        default_factory=dict,
        description="Tool result data",
    )


class CrisisInboxEnvironment(Environment):
    """
    Simulates a 48-hour post-disaster inbox triage scenario.

    Uses OpenEnv's Environment base class with HTTP transport (no MCP).
    The agent receives messages from family, employers, government agencies,
    insurance companies, and service providers. It must prioritize safety,
    meet deadlines, and adapt to changing rules (schema drift).

    Timeline engine:
    - Messages arrive at their scheduled timestamp_hours
    - Each action advances time by 0.25 hours (15 minutes)
    - Reading a message advances time by 0.1 hours (6 minutes)
    - Deadlines tick down as time passes
    - 3 random drift events fire at their trigger times

    Tools (dispatched via step()):
    - get_inbox: View messages that have arrived so far
    - read_message: Read a specific message in full
    - respond_to_message: Respond to / take action on a message
    - get_status: See current time, score, and handled messages
    - advance_time: Skip forward in time (in hours)
    - get_prompt: Get formatted triage prompt
    - score_batch: Batch-score model completions
    """

    def __init__(self):
        self._all_messages: list[Message] = []
        self._visible_messages: list[Message] = []
        self._handled: dict[str, str] = {}
        self._read_msgs: set[str] = set()
        self._current_hour: float = 0.0
        self._score: float = 0.0
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._drift_events: list[DriftEvent] = []
        self._fired_drifts: set[str] = set()
        self._superseded: dict[str, str] = {}
        self._escalation_map: dict[str, Message] = {}
        self._reply_map: dict[str, Message] = {}
        self._conflict_pairs: dict[str, str] = {}
        self._rng = random.Random()

    def get_inbox(self) -> list[dict]:
        """View all messages currently in the inbox."""
        self._deliver_messages()
        summaries = []
        for msg in self._visible_messages:
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
                "superseded": msg.id in self._superseded,
                "conflicts_with": msg.conflicts_with,
            })
        return summaries

    def read_message(self, message_id: str) -> dict:
        """Read the full content of a specific message. Costs 0.1h."""
        self._deliver_messages()
        for msg in self._visible_messages:
            if msg.id == message_id:
                self._read_msgs.add(message_id)
                self._advance_clock(0.1)
                result = msg.model_dump(exclude={"drift_flag"})
                result["current_hour"] = self._current_hour
                if msg.id in self._superseded:
                    result["WARNING"] = (
                        f"This message has been superseded by {self._superseded[msg.id]}. "
                        "Information may be outdated."
                    )
                return result
        return {"error": f"Message '{message_id}' not found or hasn't arrived yet"}

    def respond_to_message(self, message_id: str, response: str) -> dict:
        """Respond to or take action on a message. Costs 0.25h."""
        self._deliver_messages()

        msg = None
        for m in self._visible_messages:
            if m.id == message_id:
                msg = m
                break

        if msg is None:
            return {"error": f"Message '{message_id}' not found or hasn't arrived yet"}

        if message_id in self._handled:
            return {"error": f"Message '{message_id}' already handled"}

        unmet = [dep for dep in msg.dependencies if dep not in self._handled]
        if unmet:
            return {"error": f"Unmet dependencies: {unmet}. Handle those messages first."}

        reward = calculate_reward(
            msg, self._current_hour, response, self._superseded,
            self._visible_messages, self._handled,
        )
        self._handled[message_id] = response
        self._score += reward

        if msg.conflicts_with and msg.conflicts_with not in self._handled:
            self._handled[msg.conflicts_with] = "[AUTO-EXPIRED: time conflict]"

        if msg.reply_trigger and msg.reply_trigger in self._reply_map:
            reply_msg = self._reply_map[msg.reply_trigger]
            reply_msg.timestamp_hours = self._current_hour + 0.5
            if reply_msg.deadline_hours is not None and reply_msg.deadline_hours == 0.0:
                reply_msg.deadline_hours = self._current_hour + 6.0
            if not any(m.id == reply_msg.id for m in self._all_messages):
                self._all_messages.append(reply_msg)

        if message_id in self._escalation_map:
            esc = self._escalation_map[message_id]
            self._all_messages = [m for m in self._all_messages if m.id != esc.id]
            self._visible_messages = [m for m in self._visible_messages if m.id != esc.id]

        self._advance_clock(0.25)
        done = self._current_hour >= 48.0

        return {
            "status": "handled",
            "message_id": message_id,
            "reward": reward,
            "total_score": self._score,
            "current_hour": self._current_hour,
            "messages_handled": len(self._handled),
            "messages_visible": len(self._visible_messages),
            "done": done,
        }

    def get_status(self) -> dict:
        """Get current environment status."""
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

        return {
            "current_hour": self._current_hour,
            "total_score": self._score,
            "messages_total_arrived": len(self._visible_messages),
            "messages_handled": len(self._handled),
            "messages_remaining": len(self._visible_messages) - len(self._handled),
            "expired_deadlines": expired,
            "upcoming_deadlines": upcoming_deadlines,
            "drift_events_fired": len(self._fired_drifts),
            "done": self._current_hour >= 48.0,
        }

    def get_prompt(self) -> str:
        """Get a formatted triage prompt for the current inbox state.

        Only includes unhandled messages to keep prompts compact for small models.
        Handled messages are summarized as a count.
        """
        self._deliver_messages()
        hour = self._current_hour
        inbox = self._visible_messages
        unhandled = [m for m in inbox if m.id not in self._handled]
        handled_count = len(inbox) - len(unhandled)

        lines = [
            f"You are managing a crisis inbox during a natural disaster. It is hour {hour:.1f} of 48.",
            f"You have {len(unhandled)} unhandled messages ({handled_count} already handled).",
            "",
            "UNHANDLED MESSAGES:",
            "=" * 60,
        ]
        for msg in unhandled:
            superseded = " [SUPERSEDED]" if msg.id in self._superseded else ""
            conflict = f" [CONFLICTS WITH {msg.conflicts_with}]" if msg.conflicts_with else ""
            deadline_str = f", deadline: hour {msg.deadline_hours}" if msg.deadline_hours else ""
            lines.append(
                f"{msg.id} | {msg.urgency.value.upper()} | "
                f"From: {msg.sender} via {msg.channel.value} | "
                f"\"{msg.subject}\"{deadline_str}{superseded}{conflict}"
            )
        lines.extend([
            "=" * 60,
            "",
            "Choose the most important unhandled message and respond to it.",
            "Use: respond_to_message(message_id, \"your response\")",
            "Prioritize: critical > high > medium > low. Watch deadlines and policy changes.",
        ])
        return "\n".join(lines)

    def advance_time(self, hours: float) -> dict:
        """Advance the clock forward by the specified number of hours."""
        hours = max(0.5, min(4.0, hours))
        old_visible_count = len(self._visible_messages)
        self._advance_clock(hours)
        new_visible_count = len(self._visible_messages)

        return {
            "advanced_by": hours,
            "current_hour": self._current_hour,
            "new_messages": new_visible_count - old_visible_count,
            "total_visible": new_visible_count,
            "done": self._current_hour >= 48.0,
        }

    def score_batch(self, completions: list[str], prompt_data: dict) -> dict:
        """Score model completions against an inbox snapshot."""
        rewards = [score_action(c, prompt_data) for c in completions]
        return {"rewards": rewards}

    def score_completions(self, completions: list[str]) -> dict:
        """Score model completions against the CURRENT environment state.

        Used for online GRPO training — the environment provides its own
        prompt_data from its current state, so the trainer doesn't need to
        pass inbox snapshots over the network.
        """
        self._deliver_messages()
        inbox = self.get_inbox()
        prompt_data = {
            "messages": inbox,
            "hour": self._current_hour,
            "superseded": {mid: "" for mid in self._superseded},
        }
        rewards = [score_action(c, prompt_data) for c in completions]
        return {"rewards": rewards, "hour": self._current_hour, "n_messages": len(inbox)}

    def _advance_clock(self, hours: float):
        """Advance the clock and deliver any new messages/drift events."""
        self._current_hour = min(48.0, self._current_hour + hours)
        self._deliver_messages()
        self._fire_drift_events()
        self._fire_escalations()

    def _deliver_messages(self):
        """Make messages visible if their timestamp has been reached."""
        for msg in self._all_messages:
            if msg.timestamp_hours <= self._current_hour:
                if not any(m.id == msg.id for m in self._visible_messages):
                    self._visible_messages.append(msg)

    def _fire_escalations(self):
        """Inject escalation messages for unhandled messages past their deadline + delay."""
        for parent_id, esc_msg in list(self._escalation_map.items()):
            if parent_id in self._handled:
                continue  # Handled in time, no escalation
            # Find the parent message to check deadline
            parent = next((m for m in self._all_messages if m.id == parent_id), None)
            if parent is None or parent.deadline_hours is None:
                continue
            trigger_hour = parent.deadline_hours + (parent.escalation_delay_hours or 0.0)
            if self._current_hour >= trigger_hour:
                # Inject escalation message if not already present
                if not any(m.id == esc_msg.id for m in self._all_messages):
                    esc_msg.timestamp_hours = trigger_hour
                    self._all_messages.append(esc_msg)

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

    # ------------------------------------------------------------------
    # OpenEnv Environment interface
    # ------------------------------------------------------------------

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any,
    ) -> CrisisInboxObservation:
        """Reset the environment for a new episode."""
        self._rng = random.Random(seed)

        # Build the message pool: start with non-drift messages
        drift_msg_ids = set()
        self._drift_events = select_drift_events(count=3, rng=self._rng)
        for drift in self._drift_events:
            for msg in drift.messages:
                drift_msg_ids.add(msg.id)

        all_drift_ids = set()
        for drift in ALL_DRIFT_EVENTS:
            for msg in drift.messages:
                all_drift_ids.add(msg.id)

        self._all_messages = []
        for msg in ALL_MESSAGES:
            if msg.id in all_drift_ids and msg.id not in drift_msg_ids:
                continue
            m = msg.model_copy()
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

        self._escalation_map = {}
        self._reply_map = {}
        self._conflict_pairs = {}

        deferred_ids: set[str] = set()
        for m in self._all_messages:
            if m.escalation_trigger:
                deferred_ids.add(m.escalation_trigger)
            if m.reply_trigger:
                deferred_ids.add(m.reply_trigger)
            if m.conflicts_with:
                self._conflict_pairs[m.id] = m.conflicts_with

        kept: list[Message] = []
        for m in self._all_messages:
            if m.id in deferred_ids:
                for parent in self._all_messages:
                    if parent.escalation_trigger == m.id:
                        self._escalation_map[parent.id] = m
                    if parent.reply_trigger == m.id:
                        self._reply_map[m.id] = m
            else:
                kept.append(m)
        self._all_messages = kept

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

        self._deliver_messages()

        return CrisisInboxObservation(
            done=False,
            reward=0.0,
            result={
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

    def step(
        self,
        action: CrisisInboxAction,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> CrisisInboxObservation:
        """Dispatch an action to the appropriate tool method."""
        self._state.step_count += 1
        name = action.tool_name
        args = action.arguments

        if name == "get_inbox":
            result = self.get_inbox()
        elif name == "read_message":
            result = self.read_message(**args)
        elif name == "respond_to_message":
            result = self.respond_to_message(**args)
        elif name == "get_status":
            result = self.get_status()
        elif name == "get_prompt":
            result = self.get_prompt()
        elif name == "advance_time":
            result = self.advance_time(**args)
        elif name == "score_batch":
            result = self.score_batch(**args)
        elif name == "score_completions":
            result = self.score_completions(**args)
        else:
            result = {"error": f"Unknown tool: {name}"}

        # Extract reward/done from respond_to_message results
        reward = 0.0
        done = self._current_hour >= 48.0
        if isinstance(result, dict):
            reward = result.get("reward", 0.0)
            done = done or result.get("done", False)

        return CrisisInboxObservation(
            done=done,
            reward=reward,
            result=result,
        )

    @property
    def state(self) -> State:
        return self._state
