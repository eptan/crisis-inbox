"""
CrisisInbox Environment Client.

Connects to a running CrisisInbox server via WebSocket.
Provides prompt building, episode collection, and evaluation utilities.
"""

import json
import re
from typing import Any, Callable, Optional

from openenv.core.mcp_client import MCPToolClient
from openenv.core.env_server.mcp_types import CallToolAction


class CrisisInboxEnv(MCPToolClient):
    """
    Client for the CrisisInbox Environment.

    Provides MCP tool-calling interface:
    - list_tools(): Discover available tools
    - call_tool(name, **kwargs): Call a tool by name
    - reset(): Reset the environment
    - step(action): Execute an action

    Example:
        >>> with CrisisInboxEnv(base_url="http://localhost:8000") as env:
        ...     env.reset()
        ...     tools = env.list_tools()
        ...     inbox = env.call_tool("get_inbox")
        ...     print(inbox)
    """
    pass


def build_prompt(inbox: list[dict], hour: float) -> str:
    """Build a triage prompt from the current inbox state.

    Formats the inbox into a structured text prompt that instructs the
    model to pick the most important unhandled message and respond.

    Args:
        inbox: List of message dicts from the get_inbox tool.
        hour: Current simulation hour (0-48).

    Returns:
        Formatted prompt string.
    """
    lines = [
        f"You are managing a crisis inbox during a natural disaster. It is hour {hour:.1f} of 48.",
        f"You have {len(inbox)} messages. Unhandled messages need your attention.",
        "",
        "INBOX:",
        "=" * 60,
    ]
    for msg in inbox:
        status = "HANDLED" if msg.get("handled") else "UNHANDLED"
        # drift_flag intentionally not shown — agent must detect from content
        superseded = " [SUPERSEDED]" if msg.get("superseded") else ""
        deadline_str = f", deadline: hour {msg['deadline_hours']}" if msg.get("deadline_hours") else ""
        lines.append(
            f"[{status}] {msg['id']} | {msg['urgency'].upper()} | "
            f"From: {msg['sender']} via {msg['channel']} | "
            f"\"{msg['subject']}\"{deadline_str}{superseded}"
        )
    lines.extend([
        "=" * 60,
        "",
        "Choose the most important unhandled message and respond to it.",
        "Use: respond_to_message(message_id, \"your response\")",
        "Prioritize: critical > high > medium > low. Watch deadlines and policy changes.",
    ])
    return "\n".join(lines)


def collect_episode(
    base_url: str,
    seed: int,
    time_steps: Optional[list[float]] = None,
) -> dict:
    """Collect one episode from the live environment.

    Connects via WebSocket, resets with the given seed, then snapshots the
    inbox at several time points to create decision-point prompts.

    Args:
        base_url: URL of the CrisisInbox server.
        seed: Random seed for the episode.
        time_steps: Simulation hours at which to snapshot. Defaults to
                    [0, 2, 6, 12, 18, 24, 30, 36, 42, 47].

    Returns:
        Episode dict with 'episode_id', 'seed', 'decision_points', etc.
    """
    if time_steps is None:
        time_steps = [0, 2, 6, 12, 18, 24, 30, 36, 42, 47]

    superseded_msgs: dict[str, str] = {}

    with MCPToolClient(
        base_url=base_url, connect_timeout_s=60.0, message_timeout_s=120.0,
    ) as env:
        env.reset(seed=seed)
        decision_points = []
        current_hour = 0.0

        for target_hour in time_steps:
            # Advance time to reach the target hour
            while current_hour < target_hour - 0.1:
                jump = min(4.0, target_hour - current_hour)
                env.call_tool("advance_time", hours=jump)
                status_raw = env.call_tool("get_status")
                status = json.loads(status_raw) if isinstance(status_raw, str) else status_raw
                current_hour = status["current_hour"]

            # Snapshot the inbox
            inbox_raw = env.call_tool("get_inbox")
            inbox = json.loads(inbox_raw) if isinstance(inbox_raw, str) else inbox_raw

            # Track superseded messages
            for m in inbox:
                if m.get("superseded"):
                    superseded_msgs[m["id"]] = ""

            # Only create a decision point if there are unhandled messages
            unhandled = [m for m in inbox if not m.get("handled", False)]
            if not unhandled:
                continue

            prompt = build_prompt(inbox, target_hour)
            decision_points.append({
                "hour": target_hour,
                "visible_count": len(inbox),
                "prompt": prompt,
                "messages": inbox,
                "superseded": dict(superseded_msgs),
            })

    return {
        "episode_id": f"ep_{seed}",
        "seed": seed,
        "drift_events": [],
        "superseded_messages": superseded_msgs,
        "decision_points": decision_points,
    }


def extract_tool_result(obs: Any) -> dict:
    """Extract the JSON result dict from a CallToolObservation.

    obs.result may be a plain string, a dict with 'data' key (FastMCP
    CallToolResult serialization), or an object with a .data attribute.
    Normalizes to a dict.
    """
    raw = getattr(obs, "result", None)

    # FastMCP CallToolResult object -> unwrap .data
    if hasattr(raw, "data"):
        raw = raw.data

    # Serialized as {"data": "..."} dict
    if isinstance(raw, dict) and "data" in raw:
        raw = raw["data"]

    # Now raw should be a JSON string
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}

    # Already a dict
    if isinstance(raw, dict):
        return raw

    return {}


def parse_action(completion: str) -> tuple[Optional[str], str]:
    """Parse a model completion for respond_to_message(msg_id, response).

    Returns:
        Tuple of (msg_id, response_text). msg_id is None if unparseable.
    """
    match = re.search(
        r'respond_to_message\s*\(\s*["\']?(msg_\d+)["\']?\s*,\s*["\'](.+?)["\']',
        completion, re.DOTALL,
    )
    if match:
        return match.group(1), match.group(2)

    id_match = re.search(r'(msg_\d+)', completion)
    if id_match:
        return id_match.group(1), completion[:200]

    return None, ""


def evaluate_on_live_env(
    generate_fn: Callable[[str], str],
    base_url: str,
    seed: int,
    max_steps: int = 20,
    verbose: bool = True,
) -> dict:
    """Run a model against the live environment using OpenEnv's step() flow.

    Uses env.step(CallToolAction(...)) for respond_to_message so that
    rewards flow through Observation.reward — the standard OpenEnv contract.
    Read-only tools (get_inbox, get_status, advance_time) use call_tool().

    Args:
        generate_fn: Callable that takes a prompt string and returns
                     a model completion string.
        base_url: URL of the CrisisInbox server.
        seed: Random seed for the episode.
        max_steps: Maximum number of actions to take.
        verbose: Whether to print per-step results.

    Returns:
        Dict with 'seed', 'total_reward', 'actions', 'final_status'.
    """
    with MCPToolClient(
        base_url=base_url, connect_timeout_s=60.0, message_timeout_s=120.0,
    ) as env:
        env.reset(seed=seed)
        total_reward = 0.0
        actions_taken = []

        for step_i in range(max_steps):
            inbox = json.loads(env.call_tool("get_inbox"))
            status = json.loads(env.call_tool("get_status"))
            current_hour = status["current_hour"]

            if status.get("done"):
                break

            unhandled = [m for m in inbox if not m.get("handled", False)]
            if not unhandled:
                env.call_tool("advance_time", hours=2.0)
                continue

            prompt = build_prompt(inbox, current_hour)
            completion = generate_fn(prompt)
            msg_id, response_text = parse_action(completion)

            if msg_id is None:
                env.call_tool("advance_time", hours=1.0)
                continue

            # Use env.step() with CallToolAction so reward flows through
            # OpenEnv's Observation.reward — the proper RL loop contract.
            action = CallToolAction(
                tool_name="respond_to_message",
                arguments={"message_id": msg_id, "response": response_text},
            )
            step_result = env.step(action)
            obs = step_result.observation

            reward = obs.reward if obs.reward is not None else 0.0
            done = obs.done

            result_data = extract_tool_result(obs)
            if "error" in result_data:
                env.call_tool("advance_time", hours=1.0)
                continue

            total_reward += reward
            target_msg = next((m for m in inbox if m["id"] == msg_id), None)
            urgency = target_msg["urgency"] if target_msg else "?"
            actions_taken.append({
                "step": step_i,
                "hour": current_hour,
                "msg_id": msg_id,
                "urgency": urgency,
                "reward": reward,
            })
            if verbose:
                print(
                    f"  Step {step_i:2d} | Hour {current_hour:5.1f} | "
                    f"{msg_id} ({urgency:8s}) | Reward: {reward:+.1f} | "
                    f"Total: {total_reward:.1f}"
                )

            if done:
                break

        final_status = json.loads(env.call_tool("get_status"))

    return {
        "seed": seed,
        "total_reward": total_reward,
        "actions": actions_taken,
        "final_status": final_status,
    }
