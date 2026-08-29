import asyncio

from app.telegram import (
    build_help_message,
    build_intro_message,
    build_status_message,
    build_telegram_message,
)
from telegram_bot import ensure_event_loop


def test_build_telegram_message():
    jobs = [
        {
            "title": "Python Developer",
            "url": "https://example.com/job/123",
            "summary": "Vaga remota para Python",
            "source": "DuckDuckGo",
        }
    ]

    message = build_telegram_message(jobs, "python")

    assert "Python Developer" in message
    assert "https://example.com/job/123" in message
    assert "Vaga remota para Python" in message
    assert "python" in message.lower()


def test_build_intro_message_contains_greeting_and_services():
    message = build_intro_message("Eli")

    assert "Eli" in message
    assert "Skadi Hunter" in message
    assert "Vagas" in message
    assert "Suporte" in message


def test_build_help_message_contains_commands():
    message = build_help_message()

    assert "/vagas" in message
    assert "/status" in message
    assert "/help" in message


def test_build_status_message_contains_service_state():
    message = build_status_message("online", "Salvador")

    assert "online" in message.lower()
    assert "Salvador" in message


def test_ensure_event_loop_creates_loop_for_render_runtime():
    loop = ensure_event_loop()

    assert isinstance(loop, asyncio.AbstractEventLoop)
    assert asyncio.get_event_loop() is loop
