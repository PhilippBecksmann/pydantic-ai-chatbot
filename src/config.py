"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


class MissingConfigurationError(RuntimeError):
    """Raised when required application configuration is missing."""


@dataclass(frozen=True, slots=True)
class AppSettings:
    """Runtime settings for the chatbot application."""

    openai_api_key: str
    model_name: str = "openai:gpt-5-mini"
    history_limit: int = 20


MISSING_API_KEY_MESSAGE = (
    "Die Umgebungsvariable OPENAI_API_KEY fehlt. Trage sie in der Datei .env "
    "im Projektordner ein, zum Beispiel: OPENAI_API_KEY=dein_api_key. "
    "Die Datei .env darf nicht in Git eingecheckt werden."
)


def load_settings(env_file: str | Path = ".env") -> AppSettings:
    """Load settings from the environment and an optional .env file."""

    load_dotenv(dotenv_path=env_file)
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise MissingConfigurationError(MISSING_API_KEY_MESSAGE)

    return AppSettings(openai_api_key=api_key)
