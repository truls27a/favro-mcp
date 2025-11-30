"""Organization tools for Favro MCP."""

from typing import Any

from fastmcp import Context

from favro_mcp.context import get_favro_context
from favro_mcp.resolvers import OrganizationResolver
from favro_mcp.server import mcp


@mcp.tool
def list_organizations(ctx: Context) -> dict[str, Any]:
    """List all organizations accessible to the authenticated user.

    Returns:
        A list of organizations with their IDs, names, and member counts.
        Use set_organization tool to select one as the active organization.
    """
    favro_ctx = get_favro_context(ctx)
    with favro_ctx.get_client() as client:
        orgs = client.get_organizations()
        result = [
            {
                "organization_id": org.organization_id,
                "name": org.name,
                "member_count": len(org.shared_to_users),
            }
            for org in orgs
        ]
        return {"organizations": result}


@mcp.tool
def get_current_organization(ctx: Context) -> dict[str, Any]:
    """Get details of the currently selected organization.

    Returns:
        The organization details or a message if none is selected.
    """
    favro_ctx = get_favro_context(ctx)
    if not favro_ctx.current_org_id:
        return {"message": "No organization selected. Use set_organization tool first."}

    with favro_ctx.get_client() as client:
        org = client.get_organization(favro_ctx.current_org_id)
        return {
            "organization_id": org.organization_id,
            "name": org.name,
            "member_count": len(org.shared_to_users),
        }


@mcp.tool
def set_organization(org: str, ctx: Context) -> dict[str, Any]:
    """Select an organization as the active organization.

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
