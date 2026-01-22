"""Collection (folder) tools for Favro MCP."""

from typing import Any

from fastmcp import Context

from favro_mcp.context import get_favro_context
from favro_mcp.server import mcp


@mcp.tool
def list_collections(ctx: Context) -> dict[str, Any]:
    """List all collections (folders) in the organization.

    Collections are folders that contain boards. If you're looking for a board
    but can't find it with list_boards, it may be inside a collection.

    Use the collection name with list_boards(collection="name") to see
    boards inside that collection.

    Returns:
        A list of collections with their IDs and names.
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        collections = client.get_collections()
        result = [
            {
                "collection_id": col.collection_id,
                "name": col.name,
                "archived": col.archived,
            }
            for col in collections
        ]
        return {"collections": result}
