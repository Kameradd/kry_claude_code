"""Helper to synchronize Free Claude Code proxy settings with Claude CLI settings.json."""

from __future__ import annotations

import json
from pathlib import Path

from loguru import logger

from api.admin_urls import local_proxy_root_url
from cli.claude_env import CLAUDE_CODE_AUTO_COMPACT_WINDOW, claude_auth_token
from config.settings import Settings


def sync_claude_settings(settings: Settings) -> None:
    """Auto-sync proxy environment variables to the Claude CLI settings.json."""
    claude_dir = Path.home() / ".claude"
    settings_file = claude_dir / "settings.json"

    proxy_url = local_proxy_root_url(settings)
    auth_token = claude_auth_token(settings.anthropic_auth_token)

    try:
        claude_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error("Failed to create ~/.claude directory: {}", e)
        return

    data: dict = {}
    if settings_file.is_file():
        try:
            with open(settings_file, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                data = {}
        except Exception as e:
            logger.warning(
                "Failed to parse ~/.claude/settings.json, overwriting: {}", e
            )
            data = {}

    if "env" not in data or not isinstance(data["env"], dict):
        data["env"] = {}

    env = data["env"]
    env["ANTHROPIC_BASE_URL"] = proxy_url
    env["CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY"] = "1"
    env["CLAUDE_CODE_AUTO_COMPACT_WINDOW"] = CLAUDE_CODE_AUTO_COMPACT_WINDOW
    env["ANTHROPIC_AUTH_TOKEN"] = auth_token

    try:
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(
            "Successfully synchronized proxy settings to ~/.claude/settings.json"
        )
    except Exception as e:
        logger.error("Failed to write ~/.claude/settings.json: {}", e)
