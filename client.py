"""
CrisisInbox Environment Client.

Connects to a running CrisisInbox server via OpenEnv WebSocket sessions.
Provides prompt building, episode collection, and evaluation utilities.
"""

import json
import re
from typing import Any, Callable, Optional

import websockets.sync.client as ws_client


class CrisisInboxEnv:
    """
    WebSocket client for the CrisisInbox Environment (OpenEnv protocol).

    Uses OpenEnv's /ws endpoint for persistent sessions.

    Example:
        >>> with CrisisInboxEnv(base_url="http://localhost:8000") as env:
        ...     env.reset(seed=42)
        ...     inbox = env.call_tool("get_inbox")
        ...     print(inbox)
    """

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        # Convert http(s) to ws(s)
        ws_url = self.base_url.replace("https://", "wss://").replace("http://", "ws://")
        self._ws_url = f"{ws_url}/ws"
        self._ws: Any = None

    def _connect(self):
        if self._ws is None:
            self._ws = ws_client.connect(self._ws_url, open_timeout=self.timeout)

    def _send(self, msg_type: str, data: dict) -> dict:
        """Send a WebSocket message and return the response."""
        self._connect()
        self._ws.send(json.dumps({"type": msg_type, "data": data}))
        raw = self._ws.recv(timeout=self.timeout)
        resp = json.loads(raw)
        if resp.get("type") == "error":
            raise RuntimeError(f"Server error: {resp.get('data', {}).get('message', resp)}")
        return resp.get("data", resp)

    def reset(self, seed: Optional[int] = None) -> dict:
        """Reset the environment via OpenEnv WebSocket protocol."""
        data: dict[str, Any] = {}
        if seed is not None:
            data["seed"] = seed
        resp = self._send("reset", data)
        # resp is {"observation": {...}, "reward": ..., "done": ...}
        obs = resp.get("observation", resp)
        return obs

    def step(self, tool_name: str, **arguments: Any) -> dict:
        """Send an action via OpenEnv WebSocket step. Returns observation dict."""
        action = {"tool_name": tool_name, "arguments": arguments}
        resp = self._send("step", action)
        obs = resp.get("observation", resp)
        # Merge reward/done for convenience
        if "reward" in resp:
            obs["reward"] = resp["reward"]
        if "done" in resp:
            obs["done"] = resp["done"]
        return obs

    def call_tool(self, tool_name: str, **kwargs: Any) -> str:
        """Call a tool and return the result as a JSON string (convenience wrapper)."""
        obs = self.step(tool_name, **kwargs)
        result = obs.get("result", obs)
        return json.dumps(result) if isinstance(result, (dict, list)) else str(result)

    def get_state(self) -> dict:
        """Get environment state via OpenEnv WebSocket protocol."""
        self._connect()
        self._ws.send(json.dumps({"type": "state"}))
        raw = self._ws.recv(timeout=self.timeout)
        resp = json.loads(raw)
        return resp.get("data", resp)

    def close(self):
        if self._ws is not None:
            try:
                self._ws.send(json.dumps({"type": "close", "data": {}}))
            except Exception:
                pass
            try:
                self._ws.close()
            except Exception:
                pass
            self._ws = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def build_prompt(inbox: list[dict], hour: float) -> str:
    """Build a triage prompt from the current inbox state."""
    lines = [
        f"You are managing a crisis inbox during a natural disaster. It is hour {hour:.1f} of 48.",
        f"You have {len(inbox)} messages. Unhandled messages need your attention.",
        "",
        "INBOX:",
        "=" * 60,
    ]
    for msg in inbox:
        status = "HANDLED" if msg.get("handled") else "UNHANDLED"
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
    """Collect one episode from the live environment via WebSocket."""
    if time_steps is None:
        time_steps = [0, 2, 6, 12, 18, 24, 30, 36, 42, 47]

    superseded_msgs: dict[str, str] = {}

    with CrisisInboxEnv(base_url=base_url, timeout=120.0) as env:
        env.reset(seed=seed)
        decision_points = []
        current_hour = 0.0

        for target_hour in time_steps:
            while current_hour < target_hour - 0.1:
                jump = min(4.0, target_hour - current_hour)
                env.call_tool("advance_time", hours=jump)
                status = json.loads(env.call_tool("get_status"))
                current_hour = status["current_hour"]

            inbox = json.loads(env.call_tool("get_inbox"))

            for m in inbox:
                if m.get("superseded"):
                    superseded_msgs[m["id"]] = ""

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
    """Extract result dict from an observation."""
    if isinstance(obs, dict):
        result = obs.get("result", obs)
        if isinstance(result, str):
            try:
                return json.loads(result)
            except (json.JSONDecodeError, TypeError):
                return {}
        return result if isinstance(result, dict) else {}
    if isinstance(obs, str):
        try:
            return json.loads(obs)
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


def parse_action(completion: str) -> tuple[Optional[str], str]:
    """Parse a model completion for respond_to_message(msg_id, response)."""
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
    """Run a model against the live environment using OpenEnv's step() flow."""
    with CrisisInboxEnv(base_url=base_url, timeout=120.0) as env:
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

            # Use step() so reward flows through OpenEnv's observation
            obs = env.step("respond_to_message",
                           message_id=msg_id, response=response_text)
            result_data = obs.get("result", {})
            if isinstance(result_data, str):
                result_data = json.loads(result_data)

            if "error" in result_data:
                env.call_tool("advance_time", hours=1.0)
                continue

            reward = obs.get("reward", 0.0)
            done = obs.get("done", False)
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
