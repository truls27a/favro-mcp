"""Board resources for Favro MCP."""

import json

from fastmcp import Context

from favro_mcp.context import get_favro_context
from favro_mcp.server import mcp


@mcp.resource("favro://boards")
def list_boards(ctx: Context) -> str:
    """List all boards in the current organization.

    Returns a JSON array of boards with their IDs, names, and types.
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
        return json.dumps(result, indent=2)


@mcp.resource("favro://boards/{board_id}")
def get_board(board_id: str, ctx: Context) -> str:
    """Get details of a specific board including its columns.

    Args:
        board_id: The board's widget_common_id

    Returns board details with a list of columns.
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board = client.get_widget(board_id)
        columns = client.get_columns(board_id)
        return json.dumps(
            {
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
            },
            indent=2,
        )


@mcp.resource("favro://board/current")
def get_current_board(ctx: Context) -> str:
    """Get details of the currently selected board.

    Returns the board details or a message if none is selected.
    """
    favro_ctx = get_favro_context(ctx)
    if not favro_ctx.current_board_id:
        return json.dumps({"message": "No board selected. Use set_board tool first."})

    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board = client.get_widget(favro_ctx.current_board_id)
        columns = client.get_columns(favro_ctx.current_board_id)
        return json.dumps(
            {
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
            },
            indent=2,
        )
