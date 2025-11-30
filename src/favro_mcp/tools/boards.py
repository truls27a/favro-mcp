"""Board tools for Favro MCP."""

from typing import Any

from fastmcp import Context

from favro_mcp.context import get_favro_context
from favro_mcp.resolvers import BoardResolver
from favro_mcp.server import mcp


@mcp.tool
def set_board(board: str, ctx: Context) -> dict[str, Any]:
    """Select a board as the active board.

    This sets the default board for card operations.
    The board can be specified by ID or name.

    Args:
        board: Board ID or name

    Returns:
        The selected board details
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        resolver = BoardResolver(client)
        widget = resolver.resolve(board)

        # Set as current board
        favro_ctx.current_board_id = widget.widget_common_id

        return {
            "message": f"Selected board: {widget.name}",
            "widget_common_id": widget.widget_common_id,
            "name": widget.name,
            "type": widget.type,
        }
