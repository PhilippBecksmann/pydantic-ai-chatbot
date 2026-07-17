from __future__ import annotations

import os

import pytest

from src.config import MissingConfigurationError, load_settings


def test_load_settings_with_api_key(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=test-key\n", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    settings = load_settings(env_file)

    assert settings.openai_api_key == "test-key"
    assert settings.model_name == "openai:gpt-5-mini"
    assert settings.history_limit == 20


def test_load_settings_without_api_key(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    env_file = tmp_path / ".env"
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(MissingConfigurationError) as exc_info:
        load_settings(env_file)

    message = str(exc_info.value)
    assert "OPENAI_API_KEY" in message
    assert ".env" in message
    assert "Git" in message
