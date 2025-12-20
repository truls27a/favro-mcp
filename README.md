# Favro MCP

MCP server for interacting with Favro project management.

## Installation

```bash
pip install favro-mcp
```

Create a Favro API token at **Favro → My Profile → API Tokens**.

## Setup

Add to your MCP client config (replace with your credentials):

```json
{
  "mcpServers": {
    "favro": {
      "command": "favro-mcp",
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
  -- favro-mcp
```

## Tools

### Organizations

| Tool                       | Description              |
| -------------------------- | ------------------------ |
| `list_organizations`       | List all organizations   |
| `get_current_organization` | Get current organization |
| `set_organization`         | Set active organization  |

### Boards

| Tool                | Description            |
| ------------------- | ---------------------- |
| `list_boards`       | List all boards        |
| `get_board`         | Get board with columns |
| `get_current_board` | Get current board      |
| `set_board`         | Set active board       |

### Cards

| Tool                 | Description          |
| -------------------- | -------------------- |
| `list_cards`         | List cards on board  |
| `get_card_details`   | Get card details     |
| `create_card`        | Create a card        |
| `update_card`        | Update a card        |
| `move_card`          | Move card to column  |
| `assign_card`        | Assign/unassign user |
| `tag_card`           | Add/remove tag       |
| `delete_card`        | Delete a card        |
| `list_custom_fields` | List custom fields   |

### Columns

| Tool            | Description           |
| --------------- | --------------------- |
| `list_columns`  | List columns on board |
| `create_column` | Create a column       |
| `rename_column` | Rename a column       |
| `move_column`   | Move column position  |
| `delete_column` | Delete a column       |
