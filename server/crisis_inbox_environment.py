"""
CrisisInbox Environment Implementation.

An MCP environment simulating a 48-hour post-disaster inbox where an agent
must triage and respond to messages across multiple channels.
"""

import json
from typing import Any, Optional
from uuid import uuid4

from openenv.core.env_server.mcp_environment import MCPEnvironment
from openenv.core.env_server.types import Action, Observation, State
from fastmcp import FastMCP

try:
    from ..models import Channel, Message, Urgency
except ImportError:
    from models import Channel, Message, Urgency


# Seed messages for the initial scenario
SEED_MESSAGES = [
    Message(
        id="msg_001",
        sender="National Weather Service",
        channel=Channel.GOVERNMENT_ALERT,
        subject="Mandatory Evacuation Order - Zone A",
        content=(
            "A mandatory evacuation order has been issued for Zone A effective immediately. "
            "All residents must evacuate within 6 hours. Failure to comply may result in "
            "inability to receive emergency services. Evacuation shelters are open at "
            "Lincoln High School and the Convention Center."
        ),
        urgency=Urgency.CRITICAL,
        timestamp_hours=0.0,
        deadline_hours=6.0,
        drift_flag=False,
    ),
    Message(
        id="msg_002",
        sender="Mom",
        channel=Channel.SMS,
        subject="Are you safe?",
        content=(
            "Honey are you ok?? I saw the news about the hurricane. Your father and I "
            "are worried sick. Please call us when you can. We can drive down to help "
            "if you need us."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=0.5,
        drift_flag=False,
    ),
    Message(
        id="msg_003",
        sender="State Farm Insurance",
        channel=Channel.EMAIL,
        subject="Important: File your claim within 72 hours",
        content=(
            "Dear Policyholder, if you have experienced property damage due to the "
            "recent disaster, please file your claim within 72 hours to ensure timely "
            "processing. You will need: policy number, photos of damage, and a list "
            "of damaged items. File at statefarm.com/claims or call 1-800-STATE-FARM."
        ),
        urgency=Urgency.HIGH,
        timestamp_hours=1.0,
        deadline_hours=73.0,
        dependencies=[],
        drift_flag=False,
    ),
    Message(
        id="msg_004",
        sender="HR Department",
        channel=Channel.EMAIL,
        subject="Remote work policy during emergency",
        content=(
            "Due to the declared state of emergency, all employees in affected areas "
            "may work remotely. Please log into the HR portal and submit your emergency "
            "status form by end of day tomorrow. If you are unable to work, file for "
            "emergency leave. Contact your manager with your status."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=2.0,
        deadline_hours=26.0,
        drift_flag=False,
    ),
    Message(
        id="msg_005",
        sender="Delta Airlines",
        channel=Channel.APP_NOTIFICATION,
        subject="Flight DL1847 Cancelled",
        content=(
            "Your flight DL1847 on March 10 has been cancelled due to airport closure. "
            "You may rebook at no charge or request a full refund. Rebooking must be "
            "completed within 48 hours."
        ),
        urgency=Urgency.MEDIUM,
        timestamp_hours=3.0,
        deadline_hours=51.0,
        drift_flag=False,
    ),
]


class CrisisInboxEnvironment(MCPEnvironment):
    """
    Simulates a 48-hour post-disaster inbox triage scenario.

    The agent receives messages from family, employers, government agencies,
    insurance companies, and service providers. It must prioritize safety,
    meet deadlines, and adapt to changing rules (schema drift).

    MCP tools:
    - get_inbox: View current unread messages
    - read_message: Read a specific message in full
    - respond_to_message: Respond to / take action on a message
    - get_status: See current time, score, and handled messages
    """

    def __init__(self):
        mcp = FastMCP("crisis_inbox")

        # Environment state (will be set on reset)
        self._messages: list[Message] = []
        self._handled: dict[str, str] = {}  # msg_id -> response
        self._current_hour: float = 0.0
        self._score: float = 0.0
        self._state = State(episode_id=str(uuid4()), step_count=0)

        @mcp.tool
        def get_inbox() -> str:
            """
            View all messages currently in the inbox.
            Returns a JSON list of message summaries (id, sender, subject, urgency, channel, timestamp).
            """
            summaries = []
            for msg in self._messages:
                summaries.append({
                    "id": msg.id,
                    "sender": msg.sender,
                    "subject": msg.subject,
                    "urgency": msg.urgency.value,
                    "channel": msg.channel.value,
                    "timestamp_hours": msg.timestamp_hours,
                    "deadline_hours": msg.deadline_hours,
                    "handled": msg.id in self._handled,
                    "drift_flag": msg.drift_flag,
                })
            return json.dumps(summaries, indent=2)

        @mcp.tool
        def read_message(message_id: str) -> str:
            """
            Read the full content of a specific message.

            Args:
                message_id: The ID of the message to read (e.g. 'msg_001')

            Returns:
                Full message details as JSON, or error if not found.
            """
            for msg in self._messages:
                if msg.id == message_id:
                    return msg.model_dump_json(indent=2)
            return json.dumps({"error": f"Message '{message_id}' not found"})

        @mcp.tool
        def respond_to_message(message_id: str, response: str) -> str:
            """
            Respond to or take action on a message.

            Args:
                message_id: The ID of the message to respond to
                response: Your response or action description

            Returns:
                Result of the action including any reward earned.
            """
            msg = None
            for m in self._messages:
                if m.id == message_id:
                    msg = m
                    break

            if msg is None:
                return json.dumps({"error": f"Message '{message_id}' not found"})

            if message_id in self._handled:
                return json.dumps({"error": f"Message '{message_id}' already handled"})

            # Check dependencies
            unmet = [dep for dep in msg.dependencies if dep not in self._handled]
            if unmet:
                return json.dumps({
                    "error": f"Unmet dependencies: {unmet}. Handle those messages first."
                })

            # Calculate reward based on urgency and timing
            reward = _calculate_reward(msg, self._current_hour, response)
            self._handled[message_id] = response
            self._score += reward

            # Advance time slightly per action
            self._current_hour += 0.25

            done = len(self._handled) == len(self._messages) or self._current_hour >= 48.0

            return json.dumps({
                "status": "handled",
                "message_id": message_id,
                "reward": reward,
                "total_score": self._score,
                "current_hour": self._current_hour,
                "done": done,
            })

        @mcp.tool
        def get_status() -> str:
            """
            Get current environment status: time elapsed, score, and progress.
            """
            return json.dumps({
                "current_hour": self._current_hour,
                "total_score": self._score,
                "messages_total": len(self._messages),
                "messages_handled": len(self._handled),
                "messages_remaining": len(self._messages) - len(self._handled),
                "done": self._current_hour >= 48.0,
            })

        super().__init__(mcp)

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Observation:
        self._messages = [msg.model_copy() for msg in SEED_MESSAGES]
        self._handled = {}
        self._current_hour = 0.0
        self._score = 0.0
        self._state = State(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
        )

        return Observation(
            done=False,
            reward=0.0,
            metadata={
                "status": "ready",
                "message": "Crisis inbox loaded. You have 48 hours to triage incoming messages.",
                "messages_count": len(self._messages),
                "scenario": "Post-hurricane evacuation and recovery",
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


def _calculate_reward(msg: Message, current_hour: float, response: str) -> float:
    """Calculate reward for handling a message based on urgency, timing, and response quality."""
    base_rewards = {
        Urgency.CRITICAL: 10.0,
        Urgency.HIGH: 5.0,
        Urgency.MEDIUM: 3.0,
        Urgency.LOW: 1.0,
    }
    reward = base_rewards.get(msg.urgency, 1.0)

    # Bonus for handling before deadline
    if msg.deadline_hours is not None:
        if current_hour <= msg.deadline_hours:
            # Earlier = more bonus (up to 50%)
            time_remaining_frac = (msg.deadline_hours - current_hour) / msg.deadline_hours
            reward *= 1.0 + 0.5 * time_remaining_frac
        else:
            # Penalty for missing deadline
            reward *= 0.25

    # Penalty for very short/empty responses
    if len(response.strip()) < 10:
        reward *= 0.5

    # Bonus for handling drift-flagged messages (schema adaptation)
    if msg.drift_flag:
        reward *= 1.5

    return round(reward, 2)
