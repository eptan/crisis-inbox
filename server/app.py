"""
FastAPI application for the CrisisInbox Environment.

Uses OpenEnv's create_app() with Environment base class (HTTP, no MCP).

Usage:
    uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
"""

from openenv.core.env_server.http_server import create_app

try:
    from .crisis_inbox_environment import (
        CrisisInboxEnvironment,
        CrisisInboxAction,
        CrisisInboxObservation,
    )
except ImportError:
    from server.crisis_inbox_environment import (
        CrisisInboxEnvironment,
        CrisisInboxAction,
        CrisisInboxObservation,
    )

app = create_app(
    CrisisInboxEnvironment,
    CrisisInboxAction,
    CrisisInboxObservation,
    env_name="crisis_inbox",
)

# Mount demo UI
try:
    from server.demo_ui import router as demo_router
except ImportError:
    try:
        from .demo_ui import router as demo_router
    except ImportError:
        demo_router = None

if demo_router is not None:
    app.include_router(demo_router)


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
