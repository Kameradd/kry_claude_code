from __future__ import annotations

import json
from pathlib import Path

from cli.launchers.settings_sync import sync_claude_settings
from config.settings import Settings


def test_sync_creates_settings_file_if_not_exists(tmp_path: Path, monkeypatch) -> None:
    # Patch Path.home to return our tmp_path so ~/.claude is created under tmp_path
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    settings = Settings.model_construct(
        host="127.0.0.1",
        port=8082,
        anthropic_auth_token="my-test-token",
    )

    sync_claude_settings(settings)

    settings_file = tmp_path / ".claude" / "settings.json"
    assert settings_file.is_file()

    with open(settings_file, encoding="utf-8") as f:
        data = json.load(f)

    assert "env" in data
    env = data["env"]
    assert env["ANTHROPIC_BASE_URL"] == "http://127.0.0.1:8082"
    assert env["CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY"] == "1"
    assert env["ANTHROPIC_AUTH_TOKEN"] == "my-test-token"


def test_sync_preserves_existing_keys(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    settings_file = claude_dir / "settings.json"

    initial_data = {
        "apiKeyHelper": "some-script",
        "env": {
            "SOME_OTHER_VAR": "value",
            "ANTHROPIC_BASE_URL": "old-url",
        },
    }
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(initial_data, f)

    settings = Settings.model_construct(
        host="localhost",
        port=9000,
        anthropic_auth_token="",
    )

    sync_claude_settings(settings)

    with open(settings_file, encoding="utf-8") as f:
        data = json.load(f)

    assert data["apiKeyHelper"] == "some-script"
    env = data["env"]
    assert env["SOME_OTHER_VAR"] == "value"
    assert env["ANTHROPIC_BASE_URL"] == "http://localhost:9000"
    assert env["ANTHROPIC_AUTH_TOKEN"] == "fcc-no-auth"


def test_sync_handles_corrupt_json_gracefully(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    settings_file = claude_dir / "settings.json"

    with open(settings_file, "w", encoding="utf-8") as f:
        f.write("invalid json string")

    settings = Settings.model_construct(
        host="127.0.0.1",
        port=8082,
        anthropic_auth_token="token",
    )

    sync_claude_settings(settings)

    assert settings_file.is_file()
    with open(settings_file, encoding="utf-8") as f:
        data = json.load(f)

    assert "env" in data
    assert data["env"]["ANTHROPIC_AUTH_TOKEN"] == "token"
