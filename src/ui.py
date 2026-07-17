"""Gradio user interface for the chatbot."""

from __future__ import annotations

import logging
from typing import Any

import gradio as gr

from .chat_service import ChatService, ChatSession, ChatTurn, UserFacingError, to_user_error_message
from .config import AppSettings

logger = logging.getLogger(__name__)

EXAMPLES = [
    "Erklaere mir Pydantic AI einfach.",
    "Erstelle eine Python-Funktion fuer eine Einkaufsliste.",
    "Was ist der Unterschied zwischen einem Chatbot und einem KI-Agenten?",
]


def _new_session() -> ChatSession:
    return ChatSession()


async def _handle_submit(
    user_message: str,
    chatbot: list[ChatTurn] | None,
    session: ChatSession | None,
    service: ChatService,
) -> Any:
    """Handle one Gradio submit event and yield streaming UI updates."""

    current_chat = list(chatbot or [])
    current_session = session or ChatSession()
    prompt = user_message.strip()

    if not prompt:
        current_chat.append({"role": "assistant", "content": "Bitte gib eine Nachricht ein."})
        yield "", current_chat, current_session
        return

    current_chat.append({"role": "user", "content": prompt})
    current_chat.append({"role": "assistant", "content": ""})
    yield "", current_chat, current_session

    try:
        async for partial_text in service.stream_reply(prompt, current_session):
            current_chat[-1]["content"] = partial_text
            yield "", current_chat, current_session
    except UserFacingError as exc:
        current_chat[-1]["content"] = str(exc)
        yield "", current_chat, current_session
    except Exception as exc:
        logger.exception("Unhandled UI error with %s", exc.__class__.__name__)
        current_chat[-1]["content"] = to_user_error_message(exc)
        yield "", current_chat, current_session


def _reset_chat() -> tuple[list[ChatTurn], ChatSession, str]:
    """Clear the visible chat and the server-side Pydantic AI history."""

    return [], ChatSession(), ""


def create_ui(service: ChatService, settings: AppSettings) -> gr.Blocks:
    """Create the Gradio Blocks application."""

    async def submit_message(
        message: str,
        chat: list[ChatTurn] | None,
        session: ChatSession | None,
    ) -> Any:
        async for update in _handle_submit(message, chat, session, service):
            yield update

    with gr.Blocks(title="Pydantic AI Chatbot") as demo:
        gr.Markdown(
            "# Pydantic AI Chatbot\n"
            "Ein lokaler Chatbot mit Pydantic AI, OpenAI und Gradio.\n\n"
            f"**Modell:** `{settings.model_name}`\n\n"
            "Nachrichten werden zur Beantwortung an den konfigurierten KI-Anbieter uebertragen."
        )

        session_state = gr.State(_new_session())
        chatbot = gr.Chatbot(label="Chatverlauf")
        user_input = gr.Textbox(
            label="Nachricht",
            placeholder="Schreibe deine Nachricht...",
            lines=3,
        )

        with gr.Row():
            submit_button = gr.Button("Absenden", variant="primary")
            stop_button = gr.Button("Stoppen")
            reset_button = gr.Button("Chat zuruecksetzen")

        gr.Examples(examples=EXAMPLES, inputs=user_input)

        submit_event = submit_button.click(
            fn=submit_message,
            inputs=[user_input, chatbot, session_state],
            outputs=[user_input, chatbot, session_state],
        )
        input_event = user_input.submit(
            fn=submit_message,
            inputs=[user_input, chatbot, session_state],
            outputs=[user_input, chatbot, session_state],
        )

        stop_button.click(fn=None, inputs=None, outputs=None, cancels=[submit_event, input_event])
        reset_button.click(fn=_reset_chat, inputs=None, outputs=[chatbot, session_state, user_input])

    return demo
