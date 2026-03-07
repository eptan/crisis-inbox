"""
CrisisInbox Environment Client.

Connects to a running CrisisInbox server via WebSocket.
"""

from openenv.core.mcp_client import MCPToolClient


class CrisisInboxEnv(MCPToolClient):
    """
    Client for the CrisisInbox Environment.

    Provides MCP tool-calling interface:
    - list_tools(): Discover available tools
    - call_tool(name, **kwargs): Call a tool by name
    - reset(): Reset the environment
    - step(action): Execute an action

    Example:
        >>> with CrisisInboxEnv(base_url="http://localhost:8000").sync() as env:
        ...     env.reset()
        ...     tools = env.list_tools()
        ...     inbox = env.call_tool("get_inbox")
        ...     print(inbox)
    """
    pass
