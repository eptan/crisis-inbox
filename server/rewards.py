"""
CrisisInbox Reward Function — Single Source of Truth.

Both the environment server and training notebooks import from here.
No OpenEnv dependencies — only requires models.py (pydantic).
"""

import re

try:
    from ..models import Message, Urgency
except ImportError:
    from models import Message, Urgency


_FAMILY_SENDERS = {"mom", "sister", "neighbor dave", "emma"}
_FAMILY_TONE_WORDS = {"love", "safe", "worried", "sorry", "care", "okay", "miss", "hang in there"}
_FORMAL_TONE_WORDS = {"confirm", "attached", "documentation", "regarding", "request", "please", "submit"}


def tone_multiplier(sender: str, response: str) -> float:
    """
    Small reward multiplier for tone-appropriate responses.

    Family/personal senders reward empathetic language.
    Professional/institutional senders reward formal language.
    Returns 1.0-1.15 (bonus) or 1.0 (neutral). Never penalizes.
    """
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
    """
    Calculate reward for handling a message.

    Reward signals:
    - Base reward by urgency (critical=10, high=5, medium=3, low=1)
    - Deadline timing bonus (up to +50% for early, -75% for late)
    - Response quality (penalty for very short responses)
    - Tone awareness (up to +15% for matching tone to sender type)
    - Schema drift adaptation bonus (+50% for handling drift messages)
    - Penalty for acting on superseded/stale information (-50%)
    - Priority penalty (-70% for choosing low/medium when critical is pending)
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

    # Tone awareness: small bonus for matching tone to sender type
    reward *= tone_multiplier(msg.sender, response)

    # Drift adaptation bonus
    if msg.drift_flag:
        reward *= 1.5

    # Penalty for responding to a superseded message (stale info)
    if msg.id in superseded:
        reward *= 0.5

    # Conflict-resolution bonus: handling a message that forces a trade-off
    if msg.conflicts_with:
        reward *= 1.25

    # Priority penalty: choosing low/medium when unhandled critical messages exist
    if visible_messages and handled is not None:
        has_unhandled_critical = any(
            m.urgency == Urgency.CRITICAL and m.id not in handled
            for m in visible_messages
            if m.id != msg.id  # exclude the message being handled now
        )
        if has_unhandled_critical and msg.urgency in (Urgency.LOW, Urgency.MEDIUM):
            reward *= 0.3

    return round(reward, 2)


def score_action(completion: str, prompt_data: dict) -> float:
    """Score a model completion against an inbox snapshot.

    Parses the model output for respond_to_message(msg_id, response),
    constructs a Message object, and delegates to calculate_reward().

    Args:
        completion: Raw model output string.
        prompt_data: Dict with keys 'messages' (list of message dicts),
                     'hour' (float), and optionally 'superseded' (dict).

    Returns:
        Reward float. Negative for unparseable or invalid actions.
    """
    messages = prompt_data["messages"]
    hour = prompt_data["hour"]
    superseded = prompt_data.get("superseded", {})

    # Parse the model output for message_id and response text
    msg_id = None
    response_text = ""

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

    if not msg_id:
        return -1.0

    # Find the message dict in the inbox
    target_dict = None
    for msg in messages:
        if msg["id"] == msg_id:
            target_dict = msg
            break

    if target_dict is None:
        return -0.5

    # Construct a Message object for the shared reward function
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

    # Build visible_messages as Message objects for priority penalty
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

    return calculate_reward(
        msg=target_msg,
        current_hour=hour,
        response=response_text,
        superseded=superseded,
        visible_messages=visible,
        handled=handled_ids,
    )
