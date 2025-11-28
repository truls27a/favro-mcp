# Favro MCP

MCP server for interacting with Favro through Claude.

## Installation

```bash
git clone https://github.com/truls27a/favro-mcp.git
cd favro-mcp
uv sync
```

Create a Favro API token at **Favro → My Profile → API Tokens**, then create `.env`:

```bash
FAVRO_EMAIL=your-email@example.com
FAVRO_API_TOKEN=your-token
```

## Setup

Add to your MCP client config:

```json
{
  "mcpServers": {
    "favro": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/favro-mcp", "favro-mcp"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add --transport stdio favro -- uv run --directory /path/to/favro-mcp favro-mcp
```

## Resources

| Resource                    | Description             |
| --------------------------- | ----------------------- |
| `favro://organizations`     | List organizations      |
| `favro://widgets`           | List boards/backlogs    |
| `favro://widget/{id}`       | Get widget with columns |
| `favro://widget/{id}/cards` | List cards in widget    |
| `favro://card/{id}`         | Get card details        |

## Tools

| Tool               | Description                |
| ------------------ | -------------------------- |
| `set_organization` | Set active organization    |
| `search_widgets`   | Search boards by name      |
| `create_card`      | Create a card              |
| `update_card`      | Update a card              |
| `delete_card`      | Delete a card              |
| `move_card`        | Move card to column/widget |
| `add_comment`      | Add comment to card        |
