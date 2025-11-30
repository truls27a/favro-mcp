"""Base resolver class and exceptions for entity name resolution."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from favro_mcp.api.client import FavroClient

T = TypeVar("T")


class ResolverError(Exception):
    """Base exception for resolver errors."""

    pass


class NotFoundError(ResolverError):
    """Entity not found by ID or name."""

    def __init__(self, entity_type: str, identifier: str) -> None:
        self.entity_type = entity_type
        self.identifier = identifier
        super().__init__(f"{entity_type} not found: {identifier}")


class AmbiguousMatchError(ResolverError):
    """Multiple entities match the given name."""

    def __init__(
        self,
        entity_type: str,
        name: str,
        matches: list[tuple[str, str]],  # List of (id, name) tuples
    ) -> None:
        self.entity_type = entity_type
        self.name = name
        self.matches = matches

        # Format error message with all matches
        match_lines = [
            f"  - {match_id}: {match_name}" for match_id, match_name in matches
        ]
        matches_str = "\n".join(match_lines)
        super().__init__(
            f"Multiple {entity_type}s match '{name}':\n{matches_str}\n"
            f"Please use one of the IDs above instead."
        )


class BaseResolver(ABC, Generic[T]):
    """Base class for entity resolvers.

    Resolves identifiers (ID or name) to entities using auto-detection:
    1. Try to fetch by ID directly (fast path)
    2. If not found, search by name (case-insensitive)
    3. Handle duplicate names with helpful error
    """

    entity_type: str = "entity"  # Override in subclass

    def __init__(self, client: "FavroClient") -> None:
        self.client = client

    @abstractmethod
    def _fetch_all(self, **context: str | None) -> list[T]:
        """Fetch all entities of this type. Override in subclass."""
        pass

    @abstractmethod
    def _fetch_by_id(self, entity_id: str) -> T | None:
        """Fetch single entity by ID. Returns None if not found."""
        pass

    @abstractmethod
    def _get_id(self, entity: T) -> str:
        """Get the ID from an entity. Override in subclass."""
        pass

    @abstractmethod
    def _get_name(self, entity: T) -> str:
        """Get the name from an entity. Override in subclass."""
        pass

    def resolve(self, identifier: str, **context: str | None) -> T:
        """Resolve an identifier to an entity.

        Strategy:
        1. Try to fetch by ID directly (fast path)
        2. If not found, search by name
        3. Handle duplicate names with error

        Args:
            identifier: ID or name to resolve
            **context: Additional context (e.g., board_id for columns)

        Returns:
            The resolved entity

        Raises:
            NotFoundError: Entity not found
            AmbiguousMatchError: Multiple entities match
        """
        # First, try as an ID (fast path)
        try:
            entity = self._fetch_by_id(identifier)
            if entity is not None:
                return entity
        except Exception:
            pass  # Not a valid ID, try name lookup

        # Fetch all and search by name (case-insensitive)
        entities = self._fetch_all(**context)
        matches = [
            e for e in entities if self._get_name(e).lower() == identifier.lower()
        ]

        if len(matches) == 0:
            raise NotFoundError(self.entity_type, identifier)
        elif len(matches) == 1:
            return matches[0]
        else:
            # Multiple matches - provide helpful error
            match_info = [(self._get_id(e), self._get_name(e)) for e in matches]
            raise AmbiguousMatchError(self.entity_type, identifier, match_info)
