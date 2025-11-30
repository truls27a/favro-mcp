"""Card resources for Favro MCP."""

import json
from typing import Any

from fastmcp import Context

from favro_mcp.api.models import Card
from favro_mcp.context import get_favro_context
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


@mcp.resource("favro://boards/{board_id}/cards")
def list_cards(board_id: str, ctx: Context) -> str:
    """List all cards on a specific board.

    Args:
        board_id: The board's widget_common_id

    Returns a JSON array of cards with their details.
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        cards = client.get_cards(widget_common_id=board_id)
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
        return json.dumps(result, indent=2)


@mcp.resource("favro://cards/{card_id}")
def get_card(card_id: str, ctx: Context) -> str:
    """Get detailed information about a specific card.

    Args:
        card_id: The card's card_id or card_common_id

    Returns full card details including description, assignments, dates, etc.
    """
    favro_ctx = get_favro_context(ctx)
    favro_ctx.require_org()
    with favro_ctx.get_client() as client:
        card = client.get_card(card_id)
        return json.dumps(_card_to_dict(card), indent=2)
