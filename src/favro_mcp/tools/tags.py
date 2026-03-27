"""Tag tools for Favro MCP."""

from typing import Any

from fastmcp import Context

from favro_mcp.context import get_favro_context
from favro_mcp.server import mcp


@mcp.tool
def list_tags(ctx: Context) -> dict[str, Any]:
    """List all tags in the organization.

    Returns:
        A list of tags with their IDs, names, and colors.
        Use the tag name or ID with tag_card() to add/remove tags from cards.
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        tags = client.get_tags()
        result = [
            {
                "tag_id": tag.tag_id,
                "name": tag.name,
                "color": tag.color,
            }
            for tag in tags
        ]
        return {"tags": result, "count": len(result)}
