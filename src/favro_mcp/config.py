"""Configuration file management for Favro CLI."""

import os
import tomllib
from pathlib import Path
from typing import Any, TypedDict, cast


class AuthConfig(TypedDict, total=False):
    email: str
    token: str


class DefaultsConfig(TypedDict, total=False):
    organization_id: str
    board_id: str


class Config(TypedDict, total=False):
    auth: AuthConfig
    defaults: DefaultsConfig


def get_config_dir() -> Path:
    """Get the configuration directory path (XDG-compliant)."""
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        base = Path(xdg_config_home)
    else:
        base = Path.home() / ".config"
    return base / "favro-cli"


def get_config_path() -> Path:
    """Get the configuration file path."""
    return get_config_dir() / "config.toml"


def load_config() -> Config:
    """Load configuration from file. Returns empty config if file doesn't exist."""
    config_path = get_config_path()
    if not config_path.exists():
        return {}

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    # Validate and convert to typed config
    config: Config = {}

    auth_data: Any = data.get("auth")
    if isinstance(auth_data, dict):
        auth_dict = cast(dict[str, Any], auth_data)
        auth: AuthConfig = {}
        email_val: Any = auth_dict.get("email")
        token_val: Any = auth_dict.get("token")
        if email_val is not None:
            auth["email"] = str(email_val)
        if token_val is not None:
            auth["token"] = str(token_val)
        if auth:
            config["auth"] = auth

    defaults_data: Any = data.get("defaults")
    if isinstance(defaults_data, dict):
        defaults_dict = cast(dict[str, Any], defaults_data)
        defaults: DefaultsConfig = {}
        org_id_val: Any = defaults_dict.get("organization_id")
        if org_id_val is not None:
            defaults["organization_id"] = str(org_id_val)
        board_id_val: Any = defaults_dict.get("board_id")
        if board_id_val is not None:
            defaults["board_id"] = str(board_id_val)
        if defaults:
            config["defaults"] = defaults

    return config


def save_config(config: Config) -> None:
    """Save configuration to file."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    config_path = get_config_path()

    lines: list[str] = []

    if "auth" in config:
        lines.append("[auth]")
        auth = config["auth"]
        if "email" in auth:
            lines.append(f'email = "{auth["email"]}"')
        if "token" in auth:
            lines.append(f'token = "{auth["token"]}"')
        lines.append("")

    if "defaults" in config:
        lines.append("[defaults]")
        defaults = config["defaults"]
        if "organization_id" in defaults:
            lines.append(f'organization_id = "{defaults["organization_id"]}"')
        if "board_id" in defaults:
            lines.append(f'board_id = "{defaults["board_id"]}"')
        lines.append("")

    content = "\n".join(lines)
    config_path.write_text(content)


def get_credentials() -> tuple[str, str] | None:
    """Get credentials from config. Returns (email, token) or None if not configured."""
    config = load_config()
    auth = config.get("auth", {})
    email = auth.get("email")
    token = auth.get("token")

    if email and token:
        return (email, token)
    return None


def get_organization_id() -> str | None:
    """Get default organization ID from config."""
    config = load_config()
    defaults = config.get("defaults", {})
    return defaults.get("organization_id")


def set_credentials(email: str, token: str) -> None:
    """Save credentials to config."""
    config = load_config()
    config["auth"] = {"email": email, "token": token}
    save_config(config)


def set_organization_id(organization_id: str) -> None:
    """Save default organization ID to config."""
    config = load_config()
    if "defaults" not in config:
        config["defaults"] = {}
    config["defaults"]["organization_id"] = organization_id
    save_config(config)


def get_board_id() -> str | None:
    """Get default board ID from config."""
    config = load_config()
    defaults = config.get("defaults", {})
    return defaults.get("board_id")


def set_board_id(board_id: str) -> None:
    """Save default board ID to config."""
    config = load_config()
    if "defaults" not in config:
        config["defaults"] = {}
    config["defaults"]["board_id"] = board_id
    save_config(config)


def clear_credentials() -> None:
    """Remove credentials from config."""
    config = load_config()
    if "auth" in config:
        del config["auth"]
    save_config(config)
