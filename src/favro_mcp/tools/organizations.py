"""Organization tools for Favro MCP."""

from typing import Any

from fastmcp import Context

from favro_mcp.context import get_favro_context
from favro_mcp.resolvers import OrganizationResolver
from favro_mcp.server import mcp


@mcp.tool
def set_organization(org: str, ctx: Context) -> dict[str, Any]:
    """Select an organization as the active organization.

    This must be called before accessing boards, cards, or other org-specific data.
    The organization can be specified by ID or name.

    Args:
        org: Organization ID or name

    Returns:
        The selected organization details
    """
    favro_ctx = get_favro_context(ctx)
    with favro_ctx.get_client() as client:
        resolver = OrganizationResolver(client)
        organization = resolver.resolve(org)

        # Set as current org
        favro_ctx.current_org_id = organization.organization_id

        return {
            "message": f"Selected organization: {organization.name}",
            "organization_id": organization.organization_id,
            "name": organization.name,
        }
