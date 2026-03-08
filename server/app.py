"""
FastAPI application for the CrisisInbox Environment.

Usage:
    uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
    uv run --project . server
"""

from typing import Any, Dict, Union

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

    OpenEnv 0.2.1's WS handler passes a single action_cls to
    deserialize_action(), but MCPToolClient sends both ListToolsAction
    and CallToolAction through the "step" message path. Since the base
    Action model uses extra="forbid", a fixed action_cls can't handle
    both shapes. We override model_validate to route by the "type" field
    so that MCPEnvironment.step() receives the correct Action subclass.
    extra="allow" is needed because the two action types have different
    field sets.
    """

    model_config = Action.model_config.copy()
    model_config["extra"] = "allow"

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> Action:
        if isinstance(obj, dict):
            action_type = obj.get("type", "")
            if action_type == "list_tools":
                return ListToolsAction(**obj)
            elif action_type == "call_tool":
                return CallToolAction(**obj)
        return super().model_validate(obj, **kwargs)


app = create_app(
    CrisisInboxEnvironment,
    MCPAction,
    CallToolObservation,
    env_name="crisis_inbox",
)


@app.get("/health")
def health():
    return {"status": "ok"}


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
