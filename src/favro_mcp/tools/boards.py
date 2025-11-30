"""Board tools for Favro MCP."""

from typing import Any

from fastmcp import Context

from favro_mcp.context import get_favro_context
from favro_mcp.resolvers import BoardResolver
from favro_mcp.server import mcp


@mcp.tool
def list_boards(ctx: Context) -> dict[str, Any]:
    """List all boards in the current organization.

    Returns:
        A list of boards with their IDs, names, and types.
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        boards = client.get_widgets()
        result = [
            {
                "widget_common_id": board.widget_common_id,
                "name": board.name,
                "type": board.type,
                "archived": board.archived,
            }
            for board in boards
        ]
        return {"boards": result}


@mcp.tool
def get_board(board_id: str, ctx: Context) -> dict[str, Any]:
    """Get details of a specific board including its columns.

    Args:
        board_id: The board's widget_common_id

    Returns:
        Board details with a list of columns.
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board = client.get_widget(board_id)
        columns = client.get_columns(board_id)
        return {
            "widget_common_id": board.widget_common_id,
            "name": board.name,
            "type": board.type,
            "archived": board.archived,
            "color": board.color,
            "columns": [
                {
                    "column_id": col.column_id,
                    "name": col.name,
                    "position": col.position,
                    "card_count": col.card_count,
                }
                for col in sorted(columns, key=lambda c: c.position)
            ],
        }


@mcp.tool
def get_current_board(ctx: Context) -> dict[str, Any]:
    """Get details of the currently selected board.

    Returns:
        The board details or a message if none is selected.
    """
    favro_ctx = get_favro_context(ctx)
    if not favro_ctx.current_board_id:
        return {"message": "No board selected. Use set_board tool first."}

    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board = client.get_widget(favro_ctx.current_board_id)
        columns = client.get_columns(favro_ctx.current_board_id)
        return {
            "widget_common_id": board.widget_common_id,
            "name": board.name,
            "type": board.type,
            "columns": [
                {
                    "column_id": col.column_id,
                    "name": col.name,
                    "position": col.position,
                    "card_count": col.card_count,
                }
                for col in sorted(columns, key=lambda c: c.position)
            ],
        }


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
