"""FastMCP server for Favro API."""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastmcp import FastMCP

from favro_mcp.client import FavroAPIError, FavroClient

# Load environment variables
load_dotenv()

# Configure logging (stderr only, never stdout for STDIO transport)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP(name="favro-mcp")

# Global client instance (initialized lazily)
_client: FavroClient | None = None


def get_client() -> FavroClient:
    """Get or create Favro client from environment variables."""
    global _client
    if _client is None:
        email = os.getenv("FAVRO_EMAIL")
        token = os.getenv("FAVRO_API_TOKEN")
        org_id = os.getenv("FAVRO_ORGANIZATION_ID")

        if not email or not token:
            raise ValueError("FAVRO_EMAIL and FAVRO_API_TOKEN environment variables are required")

        _client = FavroClient(email=email, api_token=token, organization_id=org_id)
        logger.info(f"Initialized Favro client for {email}")

    return _client


# =============================================================================
# MCP Resources (read-only)
# =============================================================================


@mcp.resource("favro://organizations")
async def list_organizations() -> str:
    """List all accessible Favro organizations.

    Returns organization IDs and names to help identify which
    organization to use for subsequent operations.
    """
    client = get_client()
    try:
        orgs = await client.get_organizations()
        lines = ["# Organizations\n"]
        for org in orgs:
            lines.append(f"- **{org.name}** (ID: `{org.organization_id}`)")
        return "\n".join(lines)
    except FavroAPIError as e:
        return f"Error fetching organizations: {e}"


@mcp.resource("favro://organization/{org_id}")
async def get_organization(org_id: str) -> str:
    """Get details for a specific organization.

    Args:
        org_id: The organization ID
    """
    client = get_client()
    try:
        org = await client.get_organization(org_id)
        return (
            f"# {org.name}\n\n"
            f"- **Organization ID:** `{org.organization_id}`\n"
            f"- **Shared to users:** {len(org.shared_to_users)}"
        )
    except FavroAPIError as e:
        return f"Error fetching organization: {e}"


@mcp.resource("favro://widgets")
async def list_widgets() -> str:
    """List all widgets (boards/backlogs) in the current organization.

    Returns widget names, types, and IDs to help identify which
    board to use for card operations.
    """
    client = get_client()
    if not client.organization_id:
        return "Error: No organization set. Use set_organization tool first."

    try:
        widgets = await client.get_widgets()
        lines = ["# Widgets (Boards/Backlogs)\n"]
        for widget in widgets:
            status = " (archived)" if widget.archived else ""
            lines.append(
                f"- **{widget.name}** [{widget.type}]{status}\n  - ID: `{widget.widget_common_id}`"
            )
        return "\n".join(lines)
    except FavroAPIError as e:
        return f"Error fetching widgets: {e}"


@mcp.resource("favro://widget/{widget_id}")
async def get_widget(widget_id: str) -> str:
    """Get details for a specific widget.

    Args:
        widget_id: The widget common ID
    """
    client = get_client()
    if not client.organization_id:
        return "Error: No organization set. Use set_organization tool first."

    try:
        widget = await client.get_widget(widget_id)
        columns = await client.get_columns(widget_id)

        lines = [
            f"# {widget.name}\n",
            f"- **Type:** {widget.type}",
            f"- **ID:** `{widget.widget_common_id}`",
            f"- **Archived:** {widget.archived}",
            f"\n## Columns ({len(columns)})\n",
        ]

        for col in sorted(columns, key=lambda c: c.position):
            lines.append(f"- **{col.name}** ({col.card_count} cards)\n  - ID: `{col.column_id}`")

        return "\n".join(lines)
    except FavroAPIError as e:
        return f"Error fetching widget: {e}"


@mcp.resource("favro://widget/{widget_id}/columns")
async def list_widget_columns(widget_id: str) -> str:
    """List columns for a widget.

    Args:
        widget_id: The widget common ID
    """
    client = get_client()
    if not client.organization_id:
        return "Error: No organization set. Use set_organization tool first."

    try:
        columns = await client.get_columns(widget_id)
        lines = ["# Columns\n"]
        for col in sorted(columns, key=lambda c: c.position):
            lines.append(
                f"- **{col.name}**\n"
                f"  - ID: `{col.column_id}`\n"
                f"  - Cards: {col.card_count}\n"
                f"  - Position: {col.position}"
            )
        return "\n".join(lines)
    except FavroAPIError as e:
        return f"Error fetching columns: {e}"


@mcp.resource("favro://widget/{widget_id}/cards")
async def list_widget_cards(widget_id: str) -> str:
    """List all cards in a widget.

    Args:
        widget_id: The widget common ID
    """
    client = get_client()
    if not client.organization_id:
        return "Error: No organization set. Use set_organization tool first."

    try:
        cards = await client.get_cards(widget_common_id=widget_id)
        columns = await client.get_columns(widget_id)
        column_map = {col.column_id: col.name for col in columns}

        lines = [f"# Cards in Widget ({len(cards)} total)\n"]

        for card in cards:
            col_name = column_map.get(card.column_id or "", "Unknown")
            status = " (archived)" if card.archived else ""
            lines.append(
                f"## [{card.sequential_id}] {card.name}{status}\n"
                f"- **Column:** {col_name}\n"
                f"- **Card ID:** `{card.card_id}`\n"
                f"- **Common ID:** `{card.card_common_id}`"
            )
            if card.detailed_description:
                desc_preview = card.detailed_description[:200]
                if len(card.detailed_description) > 200:
                    desc_preview += "..."
                lines.append(f"- **Description:** {desc_preview}")
            if card.tags:
                lines.append(f"- **Tags:** {len(card.tags)} tags")
            lines.append("")

        return "\n".join(lines)
    except FavroAPIError as e:
        return f"Error fetching cards: {e}"


@mcp.resource("favro://card/{card_id}")
async def get_card(card_id: str) -> str:
    """Get full details for a specific card.

    Args:
        card_id: The card ID
    """
    client = get_client()
    if not client.organization_id:
        return "Error: No organization set. Use set_organization tool first."

    try:
        card = await client.get_card(card_id)

        lines = [
            f"# [{card.sequential_id}] {card.name}\n",
            f"- **Card ID:** `{card.card_id}`",
            f"- **Common ID:** `{card.card_common_id}`",
            f"- **Widget ID:** `{card.widget_common_id}`",
            f"- **Column ID:** `{card.column_id}`",
            f"- **Archived:** {card.archived}",
            f"- **Position:** {card.position}",
        ]

        if card.due_date:
            lines.append(f"- **Due Date:** {card.due_date}")
        if card.start_date:
            lines.append(f"- **Start Date:** {card.start_date}")

        lines.append("\n## Description\n")
        if card.detailed_description:
            lines.append(card.detailed_description)
        else:
            lines.append("*No description*")

        if card.tags:
            lines.append(f"\n## Tags\n{len(card.tags)} tags attached")

        if card.assignments:
            lines.append(f"\n## Assignments\n{len(card.assignments)} users assigned")

        if card.tasks_total > 0:
            lines.append(f"\n## Tasks\n{card.tasks_done}/{card.tasks_total} completed")

        if card.num_comments > 0:
            lines.append(f"\n## Comments\n{card.num_comments} comments")

        return "\n".join(lines)
    except FavroAPIError as e:
        return f"Error fetching card: {e}"


@mcp.resource("favro://column/{column_id}/cards")
async def list_column_cards(column_id: str) -> str:
    """List cards in a specific column.

    Note: This fetches all cards in the widget and filters by column.

    Args:
        column_id: The column ID
    """
    client = get_client()
    if not client.organization_id:
        return "Error: No organization set. Use set_organization tool first."

    try:
        # First get the column to find its widget
        column = await client.get_column(column_id)

        # Get all cards in the widget and filter
        all_cards = await client.get_cards(widget_common_id=column.widget_common_id)
        cards = [c for c in all_cards if c.column_id == column_id]

        lines = [f"# Cards in '{column.name}' ({len(cards)} cards)\n"]

        for card in cards:
            status = " (archived)" if card.archived else ""
            lines.append(
                f"## [{card.sequential_id}] {card.name}{status}\n- **Card ID:** `{card.card_id}`"
            )
            if card.detailed_description:
                desc_preview = card.detailed_description[:200]
                if len(card.detailed_description) > 200:
                    desc_preview += "..."
                lines.append(f"- **Description:** {desc_preview}")
            lines.append("")

        return "\n".join(lines)
    except FavroAPIError as e:
        return f"Error fetching column cards: {e}"


@mcp.resource("favro://collections")
async def list_collections() -> str:
    """List all collections (dashboards) in the organization."""
    client = get_client()
    if not client.organization_id:
        return "Error: No organization set. Use set_organization tool first."

    try:
        collections = await client.get_collections()
        lines = ["# Collections (Dashboards)\n"]
        for coll in collections:
            status = " (archived)" if coll.archived else ""
            lines.append(
                f"- **{coll.name}**{status}\n"
                f"  - ID: `{coll.collection_id}`\n"
                f"  - Widgets: {len(coll.widget_common_ids)}"
            )
        return "\n".join(lines)
    except FavroAPIError as e:
        return f"Error fetching collections: {e}"


@mcp.resource("favro://tags")
async def list_tags() -> str:
    """List all tags in the organization."""
    client = get_client()
    if not client.organization_id:
        return "Error: No organization set. Use set_organization tool first."

    try:
        tags = await client.get_tags()
        lines = ["# Tags\n"]
        for tag in tags:
            lines.append(f"- **{tag.name}** (color: {tag.color})\n  - ID: `{tag.tag_id}`")
        return "\n".join(lines)
    except FavroAPIError as e:
        return f"Error fetching tags: {e}"


# =============================================================================
# MCP Tools (mutations)
# =============================================================================


@mcp.tool()
async def set_organization(organization_id: str) -> str:
    """Set the active organization for subsequent API calls.

    This must be called before using other tools/resources that
    require an organization context.

    Args:
        organization_id: The organization ID to use
    """
    client = get_client()
    try:
        # Set the organization ID first
        client.organization_id = organization_id
        # Validate by fetching organizations list (doesn't require org header)
        orgs = await client.get_organizations()
        org = next((o for o in orgs if o.organization_id == organization_id), None)
        if org:
            return f"Organization set to: {org.name} ({organization_id})"
        else:
            client.organization_id = None
            return f"Error: Organization {organization_id} not found"
    except FavroAPIError as e:
        client.organization_id = None
        return f"Error setting organization: {e}"


@mcp.tool()
async def search_widgets(query: str) -> str:
    """Search for widgets (boards/backlogs) by name.

    Performs a case-insensitive search on widget names.

    Args:
        query: Search query to match against widget names
    """
    client = get_client()
    if not client.organization_id:
        return "Error: No organization set. Use set_organization tool first."

    try:
        widgets = await client.get_widgets()
        query_lower = query.lower()

        matches = [w for w in widgets if query_lower in w.name.lower()]

        if not matches:
            return f"No widgets found matching '{query}'"

        lines = [f"# Widgets matching '{query}' ({len(matches)} found)\n"]
        for widget in matches:
            status = " (archived)" if widget.archived else ""
            lines.append(
                f"- **{widget.name}** [{widget.type}]{status}\n  - ID: `{widget.widget_common_id}`"
            )
        return "\n".join(lines)
    except FavroAPIError as e:
        return f"Error searching widgets: {e}"


@mcp.tool()
async def create_card(
    widget_id: str,
    name: str,
    description: str | None = None,
    column_id: str | None = None,
) -> str:
    """Create a new card in a widget.

    Args:
        widget_id: The widget common ID to create the card in
        name: Card title/name
        description: Optional card description (supports markdown)
        column_id: Optional column ID (uses first column if not specified)
    """
    client = get_client()
    if not client.organization_id:
        return "Error: No organization set. Use set_organization tool first."

    try:
        card = await client.create_card(
            name=name,
            widget_common_id=widget_id,
            column_id=column_id,
            detailed_description=description,
        )
        return (
            f"Card created successfully!\n\n"
            f"- **Name:** {card.name}\n"
            f"- **Card ID:** `{card.card_id}`\n"
            f"- **Sequential ID:** {card.sequential_id}\n"
            f"- **Widget:** `{card.widget_common_id}`\n"
            f"- **Column:** `{card.column_id}`"
        )
    except FavroAPIError as e:
        return f"Error creating card: {e}"


@mcp.tool()
async def update_card(
    card_id: str,
    name: str | None = None,
    description: str | None = None,
    column_id: str | None = None,
    archived: bool | None = None,
) -> str:
    """Update an existing card.

    Args:
        card_id: The card ID to update
        name: New card title (optional)
        description: New card description (optional)
        column_id: Move to different column (optional)
        archived: Archive or unarchive the card (optional)
    """
    client = get_client()
    if not client.organization_id:
        return "Error: No organization set. Use set_organization tool first."

    try:
        # Favro API requires widgetCommonId when changing columnId
        widget_common_id = None
        if column_id:
            current_card = await client.get_card(card_id)
            widget_common_id = current_card.widget_common_id

        card = await client.update_card(
            card_id=card_id,
            name=name,
            detailed_description=description,
            column_id=column_id,
            widget_common_id=widget_common_id,
            archived=archived,
        )
        return (
            f"Card updated successfully!\n\n"
            f"- **Name:** {card.name}\n"
            f"- **Card ID:** `{card.card_id}`\n"
            f"- **Column:** `{card.column_id}`\n"
            f"- **Archived:** {card.archived}"
        )
    except FavroAPIError as e:
        return f"Error updating card: {e}"


@mcp.tool()
async def delete_card(card_id: str, everywhere: bool = False) -> str:
    """Delete a card.

    Args:
        card_id: The card ID to delete
        everywhere: If True, delete from all widgets (default: False)
    """
    client = get_client()
    if not client.organization_id:
        return "Error: No organization set. Use set_organization tool first."

    try:
        await client.delete_card(card_id=card_id, everywhere=everywhere)
        scope = "all widgets" if everywhere else "current widget"
        return f"Card `{card_id}` deleted from {scope}."
    except FavroAPIError as e:
        return f"Error deleting card: {e}"


@mcp.tool()
async def move_card(
    card_id: str,
    column_id: str | None = None,
    widget_id: str | None = None,
    position: int | None = None,
) -> str:
    """Move a card to a different column or widget.

    Args:
        card_id: The card ID to move
        column_id: Target column ID (optional)
        widget_id: Target widget ID (optional, for moving between widgets)
        position: Position in the target column (optional)
    """
    client = get_client()
    if not client.organization_id:
        return "Error: No organization set. Use set_organization tool first."

    if not column_id and not widget_id:
        return "Error: Must specify column_id and/or widget_id to move card"

    try:
        # Favro API requires widgetCommonId when changing columnId
        # If not provided, get the card's current widget
        target_widget_id = widget_id
        if column_id and not target_widget_id:
            current_card = await client.get_card(card_id)
            target_widget_id = current_card.widget_common_id

        card = await client.update_card(
            card_id=card_id,
            column_id=column_id,
            widget_common_id=target_widget_id,
            position=position,
        )
        return (
            f"Card moved successfully!\n\n"
            f"- **Name:** {card.name}\n"
            f"- **Widget:** `{card.widget_common_id}`\n"
            f"- **Column:** `{card.column_id}`\n"
            f"- **Position:** {card.position}"
        )
    except FavroAPIError as e:
        return f"Error moving card: {e}"


@mcp.tool()
async def add_comment(card_id: str, comment: str) -> str:
    """Add a comment to a card.

    Args:
        card_id: The card ID to comment on (use card_common_id)
        comment: The comment text
    """
    client = get_client()
    if not client.organization_id:
        return "Error: No organization set. Use set_organization tool first."

    try:
        # First get the card to get its card_common_id
        card = await client.get_card(card_id)

        result = await client.create_comment(
            card_common_id=card.card_common_id,
            comment=comment,
        )
        return (
            f"Comment added successfully!\n\n"
            f"- **Comment ID:** `{result.comment_id}`\n"
            f"- **Card:** `{result.card_common_id}`\n"
            f"- **Text:** {result.comment[:100]}..."
            if len(result.comment) > 100
            else f"- **Text:** {result.comment}"
        )
    except FavroAPIError as e:
        return f"Error adding comment: {e}"


@mcp.tool()
async def get_card_details(card_id: str) -> str:
    """Get detailed information about a card including description.

    This is a tool version of the card resource for easier access.

    Args:
        card_id: The card ID to fetch
    """
    client = get_client()
    if not client.organization_id:
        return "Error: No organization set. Use set_organization tool first."

    try:
        card = await client.get_card(card_id)
        comments = await client.get_comments(card.card_common_id)

        lines = [
            f"# [{card.sequential_id}] {card.name}\n",
            f"**Card ID:** `{card.card_id}`",
            f"**Common ID:** `{card.card_common_id}`",
            f"**Widget ID:** `{card.widget_common_id}`",
            f"**Column ID:** `{card.column_id}`",
            f"**Archived:** {card.archived}",
        ]

        if card.due_date:
            lines.append(f"**Due Date:** {card.due_date}")

        lines.append("\n## Description\n")
        if card.detailed_description:
            lines.append(card.detailed_description)
        else:
            lines.append("*No description*")

        if card.tasks_total > 0:
            lines.append(f"\n## Tasks: {card.tasks_done}/{card.tasks_total} completed")

        if comments:
            lines.append(f"\n## Comments ({len(comments)})\n")
            for c in comments[:5]:  # Show last 5 comments
                lines.append(f"- {c.comment[:100]}...")

        return "\n".join(lines)
    except FavroAPIError as e:
        return f"Error fetching card: {e}"
