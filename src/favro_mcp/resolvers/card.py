"""Card resolver with sequential ID support."""

import re

from favro_mcp.api.client import FavroNotFoundError
from favro_mcp.api.models import Card

from .base import AmbiguousMatchError, BaseResolver, NotFoundError


class CardResolver(BaseResolver[Card]):
    """Resolver for cards with sequential ID (#123) support.

    Supports resolution by:
    - Card ID (internal database ID)
    - Sequential ID (#123 or just 123)
    - Card name
    - Optional board_id context to narrow search scope
    """

    entity_type = "card"

    def _fetch_all(
        self, board_id: str | None = None, **context: str | None
    ) -> list[Card]:
        return self.client.get_cards(widget_common_id=board_id)

    def _fetch_by_id(self, entity_id: str) -> Card | None:
        try:
            return self.client.get_card(entity_id)
        except FavroNotFoundError:
            return None

    def _get_id(self, entity: Card) -> str:
        return entity.card_id

    def _get_name(self, entity: Card) -> str:
        return entity.name

    def _parse_sequential_id(self, identifier: str) -> int | None:
        """Parse sequential ID from various formats.

        Supported formats:
        - #123 (hash prefix)
        - 123 (plain number)
        - prefix-123 (org-specific prefix like thi-1825, Ref-17511)
        """
        # Match #123, prefix-123 (any alphabetic prefix), or just 123
        match = re.match(r"^(?:#|[a-zA-Z]+-)?(\d+)$", identifier.strip())
        if match:
            return int(match.group(1))
        return None

    def resolve(
        self, identifier: str, board_id: str | None = None, **context: str | None
    ) -> Card:
        """Resolve card identifier.

        Supports:
        - Card ID (alphanumeric)
        - Sequential ID (#123, 123, or Ref-123)
        - Card name - requires board_id

        Args:
            identifier: Card ID, sequential ID, or name
            board_id: Board ID (optional for sequential ID, required for name lookup)

        Returns:
            The resolved card

        Raises:
            NotFoundError: Card not found
            AmbiguousMatchError: Multiple cards match
            ValueError: Missing board_id for name lookup
        """
        # Check if it's a sequential ID
        seq_id = self._parse_sequential_id(identifier)
        if seq_id is not None:
            # Use cardSequentialId API parameter - more efficient than fetching all
            cards = self.client.get_cards(
                widget_common_id=board_id,  # Optional filter by board
                card_sequential_id=seq_id,
            )

            if len(cards) == 0:
                raise NotFoundError(self.entity_type, identifier)
            elif len(cards) == 1:
                return cards[0]
            else:
                # Multiple matches - shouldn't happen within an org, but handle it
                match_info = [
                    (self._get_id(c), f"#{c.sequential_id}: {self._get_name(c)}")
                    for c in cards
                ]
                raise AmbiguousMatchError(self.entity_type, identifier, match_info)

        # Try direct ID lookup first
        try:
            entity = self._fetch_by_id(identifier)
            if entity is not None:
                return entity
        except Exception:
            pass  # Not a valid ID, try name lookup

        # Name lookup requires board_id
        if board_id is None:
            raise ValueError(
                f"Card '{identifier}' not found by ID. "
                "To search by name, provide --board option"
            )

        # Fall back to name search
        cards = self._fetch_all(board_id=board_id)
        matches = [c for c in cards if self._get_name(c).lower() == identifier.lower()]

        if len(matches) == 0:
            raise NotFoundError(self.entity_type, identifier)
        elif len(matches) == 1:
            return matches[0]
        else:
            match_info = [(self._get_id(c), self._get_name(c)) for c in matches]
            raise AmbiguousMatchError(self.entity_type, identifier, match_info)
