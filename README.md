# Favro MCP

MCP server for interacting with Favro project management.

## Installation

```bash
pip install favro-mcp
```

### Getting Your Favro API Token

1. Log in to [Favro](https://favro.com/l/login)
2. Click your **username** (top-left corner)
3. Select **My Profile**
4. Go to **API Tokens**
5. Click **Create new token**
6. Give it a name (e.g., "Favro MCP") and click **Create**
7. **Copy the token** — you won't be able to see it again!

<details>
<summary><strong>Setup for Claude Code</strong></summary>

```bash
claude mcp add --transport stdio favro \
  -e FAVRO_EMAIL=your-email@example.com \
  -e FAVRO_API_TOKEN=your-token \
  -- favro-mcp
```

See [Claude Code MCP documentation](https://docs.anthropic.com/en/docs/claude-code/mcp) for more details.

</details>

<details>
<summary><strong>Setup for Claude Desktop</strong></summary>

Add the following to your `claude_desktop_config.json` (`~/Library/Application Support/Claude/` on macOS, `%APPDATA%\Claude` on Windows):

```json
{
  "mcpServers": {
    "favro": {
      "command": "/full/path/to/favro-mcp",
      "env": {
        "FAVRO_EMAIL": "your-email@example.com",
        "FAVRO_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

**Finding the full path:** Claude Desktop doesn't inherit your shell's PATH, so you need the absolute path to `favro-mcp`:

```bash
# macOS/Linux (with pip)
which favro-mcp

# Windows (PowerShell)
(Get-Command favro-mcp).Source
```

Then restart Claude Desktop.

See [Claude Desktop MCP documentation](https://support.anthropic.com/en/articles/10949351-getting-started-with-model-context-protocol-mcp-on-claude-for-desktop) for more details.

</details>

<details>
<summary><strong>Setup for Cursor</strong></summary>

Add the following to your Cursor MCP configuration file:

- **Global (all projects):** `~/.cursor/mcp.json`
- **Project-specific:** `.cursor/mcp.json` in your project root

```json
{
  "mcpServers": {
    "favro": {
      "command": "favro-mcp",
      "env": {
        "FAVRO_EMAIL": "your-email@example.com",
        "FAVRO_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

You can also open the MCP settings via Command Palette: `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows) → search "MCP" → select "View: Open MCP Settings".

After configuration, use Agent mode in Cursor's AI chat to access Favro tools.

See [Cursor MCP documentation](https://cursor.com/docs/context/mcp) for more details.

</details>

<details>
<summary><strong>Setup for VS Code</strong></summary>

Add the following to `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "favro": {
      "type": "stdio",
      "command": "favro-mcp",
      "env": {
        "FAVRO_EMAIL": "your-email@example.com",
        "FAVRO_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

Use Agent mode in GitHub Copilot Chat to access Favro tools.

See [VS Code MCP documentation](https://code.visualstudio.com/docs/copilot/customization/mcp-servers) for more details.

</details>

<details>
<summary><strong>Setup for Codex CLI</strong></summary>

Add the following to `~/.codex/config.toml`:

```toml
[mcp_servers.favro]
command = "favro-mcp"

[mcp_servers.favro.env]
FAVRO_EMAIL = "your-email@example.com"
FAVRO_API_TOKEN = "your-token-here"
```

Or add via CLI:

```bash
codex mcp add favro \
  --env FAVRO_EMAIL=your-email@example.com \
  --env FAVRO_API_TOKEN=your-token \
  -- favro-mcp
```

See [Codex MCP documentation](https://developers.openai.com/codex/mcp/) for more details.

</details>

---

## Tools

### Organizations

| Tool                       | Description              |
| -------------------------- | ------------------------ |
| `list_organizations`       | List all organizations   |
| `get_current_organization` | Get current organization |
| `set_organization`         | Set active organization  |

### Collections (Folders)

| Tool               | Description                    |
| ------------------ | ------------------------------ |
| `list_collections` | List all collections (folders) |

### Boards

| Tool                | Description            |
| ------------------- | ---------------------- |
| `list_boards`       | List boards            |
| `get_board`         | Get board with columns |
| `get_current_board` | Get current board      |
| `set_board`         | Set active board       |

### Cards

| Tool                 | Description          |
| -------------------- | -------------------- |
| `list_cards`         | List cards on board  |
| `get_card_details`   | Get card details     |
| `add_comment`        | Add a comment to card |
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

---

## Development

This project uses [uv](https://docs.astral.sh/uv/) for development.

### Setup

1. Install uv:

   **macOS / Linux:**

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   **Windows (PowerShell):**

   ```powershell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Clone the repository:

   ```bash
   git clone https://github.com/truls27a/favro-mcp.git
   cd favro-mcp
   ```

3. Install dependencies:
   ```bash
   uv sync --dev
   ```

### Running from Source

To run a local/modified version instead of the published package:

```json
{
  "mcpServers": {
    "favro": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/favro-mcp",
        "python",
        "-m",
        "favro_mcp"
      ],
      "env": {
        "FAVRO_EMAIL": "your-email@example.com",
        "FAVRO_API_TOKEN": "your-token-here"
      }
    }
  }
}
```
