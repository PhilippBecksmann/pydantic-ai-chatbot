"""Application entry point."""

from __future__ import annotations

import logging
import sys

from src.agent import create_agent
from src.chat_service import ChatService
from src.config import MissingConfigurationError, load_settings
from src.ui import create_ui


def configure_logging() -> None:
    """Configure application logging without exposing sensitive values."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def main() -> int:
    """Start the local Gradio chatbot."""

    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Pydantic AI Chatbot")

    try:
        settings = load_settings()
    except MissingConfigurationError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    agent = create_agent(settings)
    service = ChatService(agent=agent, history_limit=settings.history_limit)
    demo = create_ui(service=service, settings=settings)
    demo.launch()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
