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
        """Parse sequential ID from #123 or 123 format."""
        # Match #123 or just 123 (numeric only)
        match = re.match(r"^#?(\d+)$", identifier.strip())
        if match:
            return int(match.group(1))
        return None

    def resolve(
        self, identifier: str, board_id: str | None = None, **context: str | None
    ) -> Card:
        """Resolve card identifier.

        Supports:
        - Card ID (alphanumeric)
        - Sequential ID (#123 or 123) - requires board_id
        - Card name - requires board_id

        Args:
            identifier: Card ID, sequential ID, or name
            board_id: Board ID required for sequential ID or name lookup

        Returns:
            The resolved card

        Raises:
            NotFoundError: Card not found
            AmbiguousMatchError: Multiple cards match
            ValueError: Missing board_id for sequential ID/name lookup
        """
        # Check if it's a sequential ID
        seq_id = self._parse_sequential_id(identifier)
        if seq_id is not None:
            if board_id is None:
                raise ValueError(
                    f"Looking up card by sequential ID (#{seq_id}) requires --board option"
                )
            # Search by sequential ID
            cards = self._fetch_all(board_id=board_id)
            matches = [c for c in cards if c.sequential_id == seq_id]

            if len(matches) == 0:
                raise NotFoundError(self.entity_type, identifier)
            elif len(matches) == 1:
                return matches[0]
            else:
                # Multiple matches by sequential ID (possible if searching across boards)
                match_info = [
                    (self._get_id(c), f"#{c.sequential_id}: {self._get_name(c)}")
                    for c in matches
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
