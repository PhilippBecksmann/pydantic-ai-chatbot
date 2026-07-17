"""Chat orchestration, streaming, history handling, and user-facing errors."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

ChatTurn = dict[str, str]


class UserFacingError(RuntimeError):
    """An expected error that can be shown to the user without a stacktrace."""


@dataclass(slots=True)
class ChatSession:
    """Server-side state for one browser chat session."""

    messages: list[Any] = field(default_factory=list)


def limit_history(messages: list[Any], limit: int) -> list[Any]:
    """Return the newest messages within the configured history limit."""

    if limit <= 0:
        return []
    return messages[-limit:]


def to_user_error_message(exc: BaseException) -> str:
    """Translate technical exceptions into concise German UI messages."""

    if isinstance(exc, UserFacingError):
        return str(exc)

    chain: list[BaseException] = []
    current: BaseException | None = exc
    while current is not None:
        chain.append(current)
        current = current.__cause__ or current.__context__

    names = " ".join(error.__class__.__name__.lower() for error in chain)
    messages = " ".join(str(error).lower() for error in chain)

    if "authentication" in names or "permission" in names or "401" in messages or "api key" in messages:
        return "Der OpenAI-API-Schluessel wurde nicht akzeptiert. Bitte pruefe deinen OPENAI_API_KEY in der .env-Datei."
    if "quota" in messages or "billing" in messages or "insufficient_quota" in messages:
        return "Dein OpenAI-Konto hat aktuell keine verfuegbare API-Quote. Bitte pruefe Guthaben, Abrechnung und Projektlimits im OpenAI-Dashboard."
    if "ratelimit" in names or "rate limit" in messages or "429" in messages:
        return "Zu viele Anfragen in kurzer Zeit. Bitte versuche es spaeter erneut."
    if "timeout" in names or any(isinstance(error, TimeoutError | asyncio.TimeoutError) for error in chain):
        return "Die Anfrage hat zu lange gedauert. Bitte versuche es erneut."
    if (
        "network" in names
        or "connection" in names
        or "connect" in names
        or "connection" in messages
        or "connect" in messages
        or "unreachable" in messages
        or "all connection attempts failed" in messages
    ):
        return "Der KI-Dienst api.openai.com ist momentan nicht erreichbar. Bitte pruefe deine Netzwerkverbindung, Firewall oder Proxy-Einstellungen."
    if "unexpectedmodelbehavior" in names or "unexpected model" in messages:
        return "Die Modellantwort konnte nicht wie erwartet verarbeitet werden."

    return "Es ist ein interner Fehler aufgetreten. Bitte versuche es erneut."


class ChatService:
    """Coordinate requests between the Gradio UI and the Pydantic AI agent."""

    def __init__(self, agent: Any, history_limit: int = 20) -> None:
        self._agent = agent
        self._history_limit = history_limit

    async def stream_reply(self, user_message: str, session: ChatSession) -> AsyncIterator[str]:
        """Stream a reply for one user message and update session history when complete."""

        prompt = user_message.strip()
        if not prompt:
            raise UserFacingError("Bitte gib eine Nachricht ein.")

        logger.info("Starting chat request")
        try:
            async with self._agent.run_stream(
                prompt,
                message_history=session.messages,
            ) as result:
                async for text in result.stream_text():
                    yield text

                complete_history = result.all_messages()
                # Version 1 uses a simple message-count limit. In production, prefer
                # token-based trimming or provider-supported compaction.
                session.messages = limit_history(list(complete_history), self._history_limit)
                logger.info("Finished chat request")
        except Exception as exc:
            logger.exception("Chat request failed with %s", exc.__class__.__name__)
            raise UserFacingError(to_user_error_message(exc)) from exc

    def reset_session(self) -> ChatSession:
        """Return a fresh, empty chat session."""

        return ChatSession()
