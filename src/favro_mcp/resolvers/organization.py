"""Organization resolver."""

from favro_mcp.api.client import FavroNotFoundError
from favro_mcp.api.models import Organization

from .base import BaseResolver


class OrganizationResolver(BaseResolver[Organization]):
    """Resolver for organizations."""

    entity_type = "organization"

    def _fetch_all(self, **context: str | None) -> list[Organization]:
        return self.client.get_organizations()

    def _fetch_by_id(self, entity_id: str) -> Organization | None:
        try:
            return self.client.get_organization(entity_id)
        except FavroNotFoundError:
            return None

    def _get_id(self, entity: Organization) -> str:
        return entity.organization_id

    def _get_name(self, entity: Organization) -> str:
        return entity.name
