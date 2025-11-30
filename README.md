# Favro MCP

MCP server for interacting with Favro.

## Installation

```bash
git clone https://github.com/truls27a/favro-mcp.git
cd favro-mcp
uv sync
```

Create a Favro API token at **Favro → My Profile → API Tokens**.

## Setup

Add to your MCP client config (replace with your credentials):

```json
{
  "mcpServers": {
    "favro": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/favro-mcp", "favro-mcp"],
      "env": {
        "FAVRO_EMAIL": "your-email@example.com",
        "FAVRO_API_TOKEN": "your-token"
      }
    }
  }
}
```

### Claude Code

```bash
claude mcp add --transport stdio favro \
  -e FAVRO_EMAIL=your-email@example.com \
  -e FAVRO_API_TOKEN=your-token \
  -- uv run --directory /path/to/favro-mcp favro-mcp
```

## Resources

| Resource                         | Description              |
| -------------------------------- | ------------------------ |
| `favro://organizations`          | List all organizations   |
| `favro://organization/current`   | Get current organization |
| `favro://boards`                 | List all boards          |
| `favro://boards/{board_id}`      | Get board with columns   |
| `favro://board/current`          | Get current board        |
| `favro://boards/{board_id}/cards`   | List cards on board   |
| `favro://boards/{board_id}/columns` | List columns on board |
| `favro://cards/{card_id}`        | Get card details         |

## Tools

| Tool               | Description            |
| ------------------ | ---------------------- |
| `set_organization` | Set active organization |
| `set_board`        | Set active board       |
| `create_card`      | Create a card          |
| `update_card`      | Update a card          |
| `move_card`        | Move card to column    |
| `assign_card`      | Assign/unassign user   |
| `tag_card`         | Add/remove tag         |
| `delete_card`      | Delete a card          |
| `create_column`    | Create a column        |
| `rename_column`    | Rename a column        |
| `move_column`      | Move column position   |
| `delete_column`    | Delete a column        |
