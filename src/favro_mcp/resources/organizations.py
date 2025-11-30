"""Organization resources for Favro MCP."""

import json

from fastmcp import Context

from favro_mcp.context import get_favro_context
from favro_mcp.server import mcp


@mcp.resource("favro://organizations")
def list_organizations(ctx: Context) -> str:
    """List all organizations accessible to the authenticated user.

    Returns a JSON array of organizations with their IDs, names, and member counts.
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
        return json.dumps(result, indent=2)


@mcp.resource("favro://organization/current")
def get_current_organization(ctx: Context) -> str:
    """Get details of the currently selected organization.

    Returns the organization details or a message if none is selected.
    """
    favro_ctx = get_favro_context(ctx)
    if not favro_ctx.current_org_id:
        return json.dumps({"message": "No organization selected. Use set_organization tool first."})

    with favro_ctx.get_client() as client:
        org = client.get_organization(favro_ctx.current_org_id)
        return json.dumps(
            {
                "organization_id": org.organization_id,
                "name": org.name,
                "member_count": len(org.shared_to_users),
            },
            indent=2,
        )
