from __future__ import annotations

from collections.abc import AsyncIterator

import pytest

from src.chat_service import ChatSession
from src.config import AppSettings
from src.ui import create_ui


class FakeService:
    async def stream_reply(self, user_message: str, session: ChatSession) -> AsyncIterator[str]:
        session.messages = ["saved"]
        yield "Teilantwort"
        yield "Fertige Antwort"


@pytest.mark.asyncio
async def test_gradio_submit_event_streams_without_generic_error() -> None:
    settings = AppSettings(openai_api_key="dummy")
    demo = create_ui(FakeService(), settings)

    result = await demo.process_api(
        block_fn=1,
        inputs=["Hallo", [], ChatSession()],
        state=None,
        request=None,
    )
    next_result = await demo.process_api(
        block_fn=1,
        inputs=["Hallo", [], ChatSession()],
        state=None,
        request=None,
        iterator=result["iterator"],
    )

    assert result["data"][0] == ""
    assert result["is_generating"] is True
    assert next_result["data"][1][-1]["content"][0]["text"] == "Teilantwort"
