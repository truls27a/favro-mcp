"""Column tools for Favro MCP."""

from typing import Any

from fastmcp import Context

from favro_mcp.context import get_favro_context
from favro_mcp.resolvers import BoardResolver, ColumnResolver
from favro_mcp.server import mcp


@mcp.tool
def create_column(
    name: str,
    ctx: Context,
    board: str | None = None,
    position: int | None = None,
) -> dict[str, Any]:
    """Create a new column on a board.

    Args:
        name: Column name
        board: Board ID or name (uses current board if not specified)
        position: Position index (0-based), appends to end if not specified

    Returns:
        The created column details
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board_id = board or favro_ctx.current_board_id
        if not board_id:
            raise ValueError("No board specified and no current board selected.")
        if board:
            board_id = BoardResolver(client).resolve(board).widget_common_id

        column = client.create_column(board_id, name, position)

        return {
            "message": f"Created column: {column.name}",
            "column_id": column.column_id,
            "name": column.name,
            "position": column.position,
        }


@mcp.tool
def rename_column(
    column: str,
    name: str,
    ctx: Context,
    board: str | None = None,
) -> dict[str, Any]:
    """Rename a column.

    Args:
        column: Column ID or name
        name: New column name
        board: Board ID or name (required for name lookup)

    Returns:
        The updated column details
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board_id = board or favro_ctx.current_board_id
        if not board_id:
            raise ValueError("No board specified and no current board selected.")
        if board:
            board_id = BoardResolver(client).resolve(board).widget_common_id

        col = ColumnResolver(client).resolve(column, board_id=board_id)
        updated = client.update_column(col.column_id, name=name)

        return {
            "message": f"Renamed column to: {updated.name}",
            "column_id": updated.column_id,
            "name": updated.name,
        }


@mcp.tool
def move_column(
    column: str,
    position: int,
    ctx: Context,
    board: str | None = None,
) -> dict[str, Any]:
    """Move a column to a new position.

    Args:
        column: Column ID or name
        position: New position index (0-based)
        board: Board ID or name (required for name lookup)

    Returns:
        The updated column details
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board_id = board or favro_ctx.current_board_id
        if not board_id:
            raise ValueError("No board specified and no current board selected.")
        if board:
            board_id = BoardResolver(client).resolve(board).widget_common_id

        col = ColumnResolver(client).resolve(column, board_id=board_id)
        updated = client.update_column(col.column_id, position=position)

        return {
            "message": f"Moved column '{updated.name}' to position {position}",
            "column_id": updated.column_id,
            "position": updated.position,
        }


@mcp.tool
def delete_column(
    column: str,
    ctx: Context,
    board: str | None = None,
) -> dict[str, Any]:
    """Delete a column from a board.

    Warning: This will also delete all cards in the column!

    Args:
        column: Column ID or name
        board: Board ID or name (required for name lookup)

    Returns:
        Confirmation of deletion
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board_id = board or favro_ctx.current_board_id
        if not board_id:
            raise ValueError("No board specified and no current board selected.")
        if board:
            board_id = BoardResolver(client).resolve(board).widget_common_id

        col = ColumnResolver(client).resolve(column, board_id=board_id)
        col_name = col.name
        col_id = col.column_id

        client.delete_column(col_id)

        return {
            "message": f"Deleted column: {col_name}",
            "column_id": col_id,
        }
