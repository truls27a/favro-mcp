"""Card tools for Favro MCP."""

from typing import Any

from fastmcp import Context

from favro_mcp.api.models import Card
from favro_mcp.context import get_favro_context
from favro_mcp.resolvers import (
    BoardResolver,
    CardResolver,
    ColumnResolver,
    TagResolver,
    UserResolver,
)
from favro_mcp.server import mcp


def _card_to_dict(card: Card) -> dict[str, Any]:
    """Convert a Card to a dictionary for JSON serialization."""
    return {
        "card_id": card.card_id,
        "card_common_id": card.card_common_id,
        "sequential_id": card.sequential_id,
        "name": card.name,
        "detailed_description": card.detailed_description,
        "widget_common_id": card.widget_common_id,
        "column_id": card.column_id,
        "lane_id": card.lane_id,
        "tags": card.tags,
        "assignments": [
            {"user_id": a.user_id, "completed": a.completed} for a in card.assignments
        ],
        "start_date": card.start_date.isoformat() if card.start_date else None,
        "due_date": card.due_date.isoformat() if card.due_date else None,
        "archived": card.archived,
        "tasks_done": card.tasks_done,
        "tasks_total": card.tasks_total,
        "time_on_board": card.time_on_board,
    }


@mcp.tool
def list_cards(
    board: str,
    ctx: Context,
    column: str | None = None,
    page: int = 0,
) -> dict[str, Any]:
    """List cards on a specific board with pagination.

    Args:
        board: The board's widget_common_id, name, or ID
        column: Optional column ID or name to filter by
        page: Page number (0-indexed, default 0). Each page contains up to 100 cards.

    Returns:
        A list of cards with pagination metadata.
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board_id = BoardResolver(client).resolve(board).widget_common_id

        # Resolve column if provided
        column_id = None
        if column:
            column_id = ColumnResolver(client).resolve(column, board_id=board_id).column_id

        cards, total_pages = client.get_cards_page(
            widget_common_id=board_id,
            column_id=column_id,
            page=page,
        )

        result = [
            {
                "card_id": card.card_id,
                "sequential_id": card.sequential_id,
                "name": card.name,
                "column_id": card.column_id,
                "tags": card.tags,
                "archived": card.archived,
            }
            for card in cards
        ]
        return {
            "cards": result,
            "page": page,
            "total_pages": total_pages,
            "cards_on_page": len(result),
        }


@mcp.tool
def get_card_details(card: str, ctx: Context, board: str | None = None) -> dict[str, Any]:
    """Get detailed information about a specific card.

    Args:
        card: Card ID, sequential ID (#123), or name
        board: Board ID or name (needed for name lookups)

    Returns:
        Full card details including description, assignments, dates, etc.
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board_id = board or favro_ctx.current_board_id
        if board:
            board_id = BoardResolver(client).resolve(board).widget_common_id
        c = CardResolver(client).resolve(card, board_id=board_id)
        return _card_to_dict(c)


@mcp.tool
def create_card(
    name: str,
    ctx: Context,
    board: str | None = None,
    column: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    assignees: list[str] | None = None,
) -> dict[str, Any]:
    """Create a new card.

    Args:
        name: Card name/title
        board: Board ID or name (uses current board if not specified)
        column: Column ID or name to place the card in
        description: Detailed description (supports markdown)
        tags: List of tag IDs or names to add
        assignees: List of user IDs, names, or emails to assign

    Returns:
        The created card details
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board_id = board or favro_ctx.current_board_id
        if not board_id:
            raise ValueError("No board specified and no current board selected.")
        if board:
            board_id = BoardResolver(client).resolve(board).widget_common_id

        # Resolve column if provided
        column_id = None
        if column:
            column_id = ColumnResolver(client).resolve(column, board_id=board_id).column_id

        # Resolve tags if provided
        tag_ids = None
        if tags:
            tag_resolver = TagResolver(client)
            tag_ids = [tag_resolver.resolve(t).tag_id for t in tags]

        # Resolve assignees if provided
        user_ids = None
        if assignees:
            user_resolver = UserResolver(client)
            user_ids = [user_resolver.resolve(u).user_id for u in assignees]

        card = client.create_card(
            name=name,
            widget_common_id=board_id,
            column_id=column_id,
            detailed_description=description,
            tags=tag_ids,
            assignments=user_ids,
        )

        return {
            "message": f"Created card #{card.sequential_id}: {card.name}",
            "card_id": card.card_id,
            "card_common_id": card.card_common_id,
            "sequential_id": card.sequential_id,
            "name": card.name,
        }


@mcp.tool
def update_card(
    card: str,
    ctx: Context,
    board: str | None = None,
    name: str | None = None,
    description: str | None = None,
    archived: bool | None = None,
) -> dict[str, Any]:
    """Update a card's properties.

    Args:
        card: Card ID, sequential ID (#123), or name
        board: Board ID or name (needed for sequential ID or name lookup)
        name: New card name
        description: New detailed description
        archived: Archive or unarchive the card

    Returns:
        The updated card details
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board_id = board or favro_ctx.current_board_id
        if board:
            board_id = BoardResolver(client).resolve(board).widget_common_id

        c = CardResolver(client).resolve(card, board_id=board_id)

        updated = client.update_card(
            card_id=c.card_id,
            name=name,
            detailed_description=description,
            archived=archived,
        )

        return {
            "message": f"Updated card: {updated.name}",
            "card_id": updated.card_id,
            "sequential_id": updated.sequential_id,
            "name": updated.name,
        }


@mcp.tool
def move_card(
    card: str,
    column: str,
    ctx: Context,
    board: str | None = None,
) -> dict[str, Any]:
    """Move a card to a different column.

    Args:
        card: Card ID, sequential ID (#123), or name
        column: Target column ID or name
        board: Board ID or name (needed for name lookups)

    Returns:
        The updated card details
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board_id = board or favro_ctx.current_board_id
        if board:
            board_id = BoardResolver(client).resolve(board).widget_common_id

        c = CardResolver(client).resolve(card, board_id=board_id)

        # Use the card's board if not specified
        target_board = board_id or c.widget_common_id
        if not target_board:
            raise ValueError("Board ID required to resolve column")

        col = ColumnResolver(client).resolve(column, board_id=target_board)
        updated = client.update_card(
            card_id=c.card_id,
            column_id=col.column_id,
            widget_common_id=target_board,
        )

        return {
            "message": f"Moved card '{updated.name}' to column '{col.name}'",
            "card_id": updated.card_id,
            "column_id": col.column_id,
            "column_name": col.name,
        }


@mcp.tool
def assign_card(
    card: str,
    user: str,
    ctx: Context,
    board: str | None = None,
    remove: bool = False,
) -> dict[str, Any]:
    """Assign or unassign a user from a card.

    Args:
        card: Card ID, sequential ID (#123), or name
        user: User ID, name, or email
        board: Board ID or name (needed for name lookups)
        remove: If True, remove the assignment instead of adding

    Returns:
        The updated card details
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board_id = board or favro_ctx.current_board_id
        if board:
            board_id = BoardResolver(client).resolve(board).widget_common_id

        c = CardResolver(client).resolve(card, board_id=board_id)
        u = UserResolver(client).resolve(user)

        if remove:
            updated = client.update_card(card_id=c.card_id, remove_assignments=[u.user_id])
            action = "Unassigned"
            prep = "from"
        else:
            updated = client.update_card(card_id=c.card_id, add_assignments=[u.user_id])
            action = "Assigned"
            prep = "to"

        return {
            "message": f"{action} {u.name} {prep} card '{updated.name}'",
            "card_id": updated.card_id,
            "user_id": u.user_id,
            "user_name": u.name,
        }


@mcp.tool
def tag_card(
    card: str,
    tag: str,
    ctx: Context,
    board: str | None = None,
    remove: bool = False,
) -> dict[str, Any]:
    """Add or remove a tag from a card.

    Args:
        card: Card ID, sequential ID (#123), or name
        tag: Tag ID or name
        board: Board ID or name (needed for name lookups)
        remove: If True, remove the tag instead of adding

    Returns:
        The updated card details
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board_id = board or favro_ctx.current_board_id
        if board:
            board_id = BoardResolver(client).resolve(board).widget_common_id

        c = CardResolver(client).resolve(card, board_id=board_id)
        t = TagResolver(client).resolve(tag)

        if remove:
            updated = client.update_card(card_id=c.card_id, remove_tags=[t.tag_id])
            action = "Removed"
            prep = "from"
        else:
            updated = client.update_card(card_id=c.card_id, add_tags=[t.tag_id])
            action = "Added"
            prep = "to"

        return {
            "message": f"{action} tag '{t.name}' {prep} card '{updated.name}'",
            "card_id": updated.card_id,
            "tag_id": t.tag_id,
            "tag_name": t.name,
        }


@mcp.tool
def delete_card(
    card: str,
    ctx: Context,
    board: str | None = None,
    everywhere: bool = False,
) -> dict[str, Any]:
    """Delete a card.

    Args:
        card: Card ID, sequential ID (#123), or name
        board: Board ID or name (needed for name lookups)
        everywhere: If True, delete from all boards (not just current)

    Returns:
        Confirmation of deletion
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board_id = board or favro_ctx.current_board_id
        if board:
            board_id = BoardResolver(client).resolve(board).widget_common_id

        c = CardResolver(client).resolve(card, board_id=board_id)
        card_name = c.name
        card_id = c.card_id

        client.delete_card(card_id, everywhere=everywhere)

        return {
            "message": f"Deleted card: {card_name}",
            "card_id": card_id,
        }
