"""User resolver (supports ID, name, and email)."""

from favro_mcp.api.client import FavroNotFoundError
from favro_mcp.api.models import User

from .base import AmbiguousMatchError, BaseResolver, NotFoundError


class UserResolver(BaseResolver[User]):
    """Resolver for users.

    Supports resolution by:
    - User ID
    - User name
    - Email address
    """

    entity_type = "user"

    def _fetch_all(self, **context: str | None) -> list[User]:
        return self.client.get_users()

    def _fetch_by_id(self, entity_id: str) -> User | None:
        try:
            return self.client.get_user(entity_id)
        except FavroNotFoundError:
            return None

    def _get_id(self, entity: User) -> str:
        return entity.user_id

    def _get_name(self, entity: User) -> str:
        return entity.name

    def resolve(self, identifier: str, **context: str | None) -> User:
        """Resolve user by ID, name, or email.

        Args:
            identifier: User ID, name, or email address

        Returns:
            The resolved user

        Raises:
            NotFoundError: User not found
            AmbiguousMatchError: Multiple users match
        """
        # Try base resolution first (ID then name)
        try:
            return super().resolve(identifier, **context)
        except NotFoundError:
            pass  # Not found by ID or name, try email

        # Try email match
        users = self._fetch_all()
        email_matches = [u for u in users if u.email.lower() == identifier.lower()]

        if len(email_matches) == 1:
            return email_matches[0]
        elif len(email_matches) > 1:
            match_info = [
                (self._get_id(u), f"{u.name} ({u.email})") for u in email_matches
            ]
            raise AmbiguousMatchError(self.entity_type, identifier, match_info)

        # Not found by any method
        raise NotFoundError(self.entity_type, identifier)
