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


def _strip_tasklist_from_description(
    description: str | None,
    tasklists: list[dict[str, Any]],
) -> str | None:
    """Strip auto-appended tasklist checkboxes from description.

    Favro's API appends tasklist items as checkbox characters to the
    detailedDescription field. This function removes those trailing
    lines to prevent duplication when updating.

    Args:
        description: The card's detailed description
        tasklists: List of tasklist dicts with 'name' and 'tasks' keys

    Returns:
        The description with trailing tasklist checkboxes removed
    """
    if not description or not tasklists:
        return description

    lines = description.rstrip().split("\n")

    # Build set of expected checkbox patterns
    checkbox_patterns: set[str] = set()
    tasklist_names: set[str] = set()
    for tasklist in tasklists:
        tasklist_names.add(tasklist.get("name", ""))
        for task in tasklist.get("tasks", []):
            task_name = task.get("name", "")
            checkbox_patterns.add(f"☐ {task_name}")
            checkbox_patterns.add(f"☑ {task_name}")

    # Strip trailing lines that match tasklist/task patterns
    while lines:
        line = lines[-1].strip()
        if not line:
            lines.pop()
        elif line in checkbox_patterns or line in tasklist_names:
            lines.pop()
        else:
            break

    return "\n".join(lines) if lines else ""


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
        "custom_fields": [
            {
                "custom_field_id": cf.custom_field_id,
                "value": cf.value,
                "total": cf.total,
                "link": cf.link,
                "members": cf.members,
                "color": cf.color,
            }
            for cf in card.custom_fields
        ],
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
def list_custom_fields(
    ctx: Context,
    name: str | None = None,
    field_type: str | None = None,
) -> dict[str, Any]:
    """List custom fields in the organization.

    Args:
        name: Filter by name (case-insensitive substring match)
        field_type: Filter by type (e.g., "Link", "Text", "Rating", "Single select")

    Returns:
        Custom field definitions with IDs, names, and types.
        Use the customFieldId when updating card custom fields.
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        fields = client.get_custom_fields()

        # Apply filters
        if name:
            name_lower = name.lower()
            fields = [f for f in fields if name_lower in f.get("name", "").lower()]
        if field_type:
            type_lower = field_type.lower()
            fields = [f for f in fields if f.get("type", "").lower() == type_lower]

        # Return minimal info
        result = [
            {"customFieldId": f["customFieldId"], "name": f["name"], "type": f["type"]}
            for f in fields
        ]
        return {"custom_fields": result, "count": len(result)}


@mcp.tool
def get_card_details(card: str, ctx: Context, board: str | None = None) -> dict[str, Any]:
    """Get detailed information about a specific card.

    Args:
        card: Card ID, sequential ID (#123), or name
        board: Board ID or name (needed for name lookups)

    Returns:
        Full card details including description, assignments, dates, custom fields,
        and task lists with their tasks.
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        board_id = board or favro_ctx.current_board_id
        if board:
            board_id = BoardResolver(client).resolve(board).widget_common_id
        c = CardResolver(client).resolve(card, board_id=board_id)

        # Fetch task lists and their tasks
        tasklists_data: list[dict[str, Any]] = []
        tasklists = client.get_tasklists(c.card_common_id)
        for tasklist in tasklists:
            tasks = client.get_tasks(c.card_common_id, tasklist.tasklist_id)
            tasklists_data.append(
                {
                    "tasklist_id": tasklist.tasklist_id,
                    "name": tasklist.name,
                    "position": tasklist.position,
                    "tasks": [
                        {
                            "task_id": task.task_id,
                            "name": task.name,
                            "completed": task.completed,
                            "position": task.position,
                        }
                        for task in tasks
                    ],
                }
            )

        result = _card_to_dict(c)
        result["tasklists"] = tasklists_data
        # Clean description to remove auto-appended tasklist checkboxes
        result["detailed_description"] = _strip_tasklist_from_description(
            result["detailed_description"], tasklists_data
        )
        return result


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
    custom_fields: list[dict[str, Any]] | None = None,
    tasks: list[dict[str, Any]] | None = None,
    add_tasklist: str | None = None,
    add_task: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Update a card's properties.

    Args:
        card: Card ID, sequential ID (#123), or name
        board: Board ID or name (needed for sequential ID or name lookup)
        name: New card name
        description: New detailed description
        archived: Archive or unarchive the card
        custom_fields: List of custom field updates. Each dict should contain
            'customFieldId' and the appropriate value field for the field type:
            - Text: {'customFieldId': '...', 'value': 'text'}
            - Number/Rating: {'customFieldId': '...', 'total': 5}
            - Link: {'customFieldId': '...', 'link': {'url': '...', 'text': '...'}}
            - Checkbox: {'customFieldId': '...', 'value': True}
            - Date: {'customFieldId': '...', 'value': '2024-01-15'}
            - Status: {'customFieldId': '...', 'value': ['itemId1', 'itemId2']}
        tasks: List of task updates. Each dict should contain 'task_id' and optionally
            'completed' (bool) or 'name' (str) to update
        add_tasklist: Name of a new task list to create on this card
        add_task: Create a new task: {'tasklist_id': '...', 'name': '...'}

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

        # Update the card itself
        updated = client.update_card(
            card_id=c.card_id,
            name=name,
            detailed_description=description,
            archived=archived,
            custom_fields=custom_fields,
        )

        messages = [f"Updated card: {updated.name}"]

        # Update tasks if specified
        if tasks:
            for task_update in tasks:
                task_id = task_update.get("task_id")
                if not task_id:
                    continue
                client.update_task(
                    task_id=task_id,
                    name=task_update.get("name"),
                    completed=task_update.get("completed"),
                )
            messages.append(f"Updated {len(tasks)} task(s)")

        # Create new task list if specified
        if add_tasklist:
            new_tasklist = client.create_tasklist(c.card_common_id, add_tasklist)
            messages.append(f"Created task list: {new_tasklist.name}")

        # Create new task if specified
        if add_task:
            tasklist_id = add_task.get("tasklist_id")
            task_name = add_task.get("name")
            if tasklist_id and task_name:
                new_task = client.create_task(tasklist_id, task_name)
                messages.append(f"Created task: {new_task.name}")

        return {
            "message": "; ".join(messages),
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
