from app.telegram import build_telegram_message


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
