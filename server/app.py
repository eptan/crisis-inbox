"""
FastAPI application for the CrisisInbox Environment.

Usage:
    uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
    uv run --project . server
"""

import json as _json
from typing import Any, Dict, Union

from pydantic import Field

from openenv.core.env_server.http_server import create_app
from openenv.core.env_server.mcp_types import (
    CallToolAction,
    CallToolObservation,
    ListToolsAction,
)
from openenv.core.env_server.types import Action

try:
    from .crisis_inbox_environment import CrisisInboxEnvironment
except ImportError:
    from server.crisis_inbox_environment import CrisisInboxEnvironment


class MCPAction(Action):
    """Action class that deserializes both ListToolsAction and CallToolAction.

    Exposes tool_name and arguments fields so the OpenEnv web UI renders
    an interactive form. Also routes ListToolsAction via model_validate
    for programmatic clients.
    """

    model_config = Action.model_config.copy()
    model_config["extra"] = "allow"

    type: str = Field(default="call_tool", description="Action type: 'call_tool' or 'list_tools'")
    tool_name: str = Field(
        default="get_inbox",
        description="Tool to call: get_inbox, read_message, respond_to_message, get_status, advance_time",
    )
    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description='Tool arguments as JSON (e.g. {"message_id": "msg_001"} or {"message_id": "msg_001", "response": "On my way"})',
    )

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> Action:
        if isinstance(obj, dict):
            action_type = obj.get("type", "")
            if action_type == "list_tools":
                return ListToolsAction(**obj)

            # Parse arguments if the web UI sent them as a JSON string
            args = obj.get("arguments", {})
            if isinstance(args, str):
                try:
                    obj = {**obj, "arguments": _json.loads(args) if args.strip() else {}}
                except _json.JSONDecodeError:
                    obj = {**obj, "arguments": {}}

            if action_type == "call_tool" or "tool_name" in obj:
                obj.setdefault("type", "call_tool")
                return CallToolAction(**{k: v for k, v in obj.items()
                                        if k in ("type", "tool_name", "arguments", "metadata")})
        return super().model_validate(obj, **kwargs)


app = create_app(
    CrisisInboxEnvironment,
    MCPAction,
    CallToolObservation,
    env_name="crisis_inbox",
)

# Mount Gradio demo UI at /demo
try:
    import gradio as gr
    from server.demo_ui import build_demo
except ImportError:
    try:
        from .demo_ui import build_demo
        import gradio as gr
    except ImportError:
        build_demo = None

if build_demo is not None:
    demo = build_demo()
    app = gr.mount_gradio_app(app, demo, path="/demo", root_path="/demo")


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
