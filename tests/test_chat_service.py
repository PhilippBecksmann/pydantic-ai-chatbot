from __future__ import annotations

from collections.abc import AsyncIterator

import pytest

from src.chat_service import ChatService, ChatSession, UserFacingError, limit_history, to_user_error_message


class FakeResult:
    def __init__(self, chunks: list[str], messages: list[object]) -> None:
        self._chunks = chunks
        self._messages = messages

    async def stream_text(self) -> AsyncIterator[str]:
        for chunk in self._chunks:
            yield chunk

    def all_messages(self) -> list[object]:
        return self._messages


class FakeStreamContext:
    def __init__(self, result: FakeResult) -> None:
        self._result = result

    async def __aenter__(self) -> FakeResult:
        return self._result

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None


class FakeAgent:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[object]]] = []

    def run_stream(self, prompt: str, message_history: list[object]) -> FakeStreamContext:
        self.calls.append((prompt, message_history))
        return FakeStreamContext(FakeResult(["Hallo", "Hallo Welt"], list(range(25))))


class BrokenAgent:
    def run_stream(self, prompt: str, message_history: list[object]) -> FakeStreamContext:
        raise TimeoutError("request timeout")


@pytest.mark.asyncio
async def test_empty_input_does_not_call_agent() -> None:
    agent = FakeAgent()
    service = ChatService(agent)

    with pytest.raises(UserFacingError) as exc_info:
        async for _ in service.stream_reply("   ", ChatSession()):
            pass

    assert "Nachricht" in str(exc_info.value)
    assert agent.calls == []


def test_limit_history_keeps_newest_messages() -> None:
    messages = list(range(25))

    limited = limit_history(messages, 20)

    assert limited == list(range(5, 25))


def test_error_mapping_for_timeout() -> None:
    message = to_user_error_message(TimeoutError("request timeout"))

    assert "zu lange" in message


def test_error_mapping_for_rate_limit() -> None:
    class RateLimitError(Exception):
        pass

    message = to_user_error_message(RateLimitError("429"))

    assert "Zu viele Anfragen" in message


def test_error_mapping_for_quota_and_billing() -> None:
    message = to_user_error_message(
        RuntimeError("You exceeded your current quota, please check your plan and billing details.")
    )

    assert "keine verfuegbare API-Quote" in message


def test_error_mapping_for_nested_model_connection_error() -> None:
    low_level = ConnectionError("All connection attempts failed")
    model_error = RuntimeError("Connection error.")
    model_error.__cause__ = low_level

    message = to_user_error_message(model_error)

    assert "nicht erreichbar" in message


@pytest.mark.asyncio
async def test_streaming_updates_session_history() -> None:
    agent = FakeAgent()
    service = ChatService(agent, history_limit=20)
    session = ChatSession(messages=["old"])

    chunks = []
    async for chunk in service.stream_reply("Hallo", session):
        chunks.append(chunk)

    assert chunks == ["Hallo", "Hallo Welt"]
    assert agent.calls == [("Hallo", ["old"])]
    assert session.messages == list(range(5, 25))


@pytest.mark.asyncio
async def test_streaming_error_becomes_user_facing_error() -> None:
    service = ChatService(BrokenAgent())

    with pytest.raises(UserFacingError) as exc_info:
        async for _ in service.stream_reply("Hallo", ChatSession()):
            pass

    assert "zu lange" in str(exc_info.value)
