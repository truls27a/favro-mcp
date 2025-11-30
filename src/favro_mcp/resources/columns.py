"""Column resources for Favro MCP."""

import json

from fastmcp import Context

from favro_mcp.context import get_favro_context
from favro_mcp.server import mcp


@mcp.resource("favro://boards/{board_id}/columns")
def list_columns(board_id: str, ctx: Context) -> str:
    """List all columns on a specific board.

    Args:
        board_id: The board's widget_common_id

    Returns a JSON array of columns sorted by position.
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        columns = client.get_columns(board_id)
        result = [
            {
                "column_id": col.column_id,
                "name": col.name,
                "position": col.position,
                "card_count": col.card_count,
            }
            for col in sorted(columns, key=lambda c: c.position)
        ]
        return json.dumps(result, indent=2)
