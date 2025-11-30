"""Favro MCP Server."""

from fastmcp import FastMCP

from favro_mcp.context import app_lifespan

mcp = FastMCP(
    name="favro-mcp",
    instructions=(
        "MCP server for Favro project management. "
        "Use resources to read data and tools to make changes. "
    ),
    lifespan=app_lifespan,
)

# Import resources and tools to register them with the server
# These imports have side effects (registering decorators with mcp)
from favro_mcp import resources as _resources  # noqa: E402, F401
from favro_mcp import tools as _tools  # noqa: E402, F401

__all__ = ["mcp", "_resources", "_tools"]
