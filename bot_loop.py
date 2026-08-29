from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

from app.search import search_jobs
from app.telegram import build_telegram_message, send_telegram_message
from telegram_bot import main as run_telegram_bot

DEFAULT_KEYWORDS = [
    "estagio suporte ti",
    "help desk",
    "suporte tecnico",
    "suporte de ti",
    "analista de suporte",
]

STATE_FILE = Path(os.getenv("JOB_STATE_FILE", "sent_jobs.json"))
LOCATION = os.getenv("JOB_LOCATION", "Salvador")
INTERVAL_SECONDS = int(os.getenv("BOT_INTERVAL_SECONDS", str(5 * 60 * 60)))
MAX_RESULTS = int(os.getenv("JOB_MAX_RESULTS", "8"))


def load_sent_urls() -> set[str]:
    if not STATE_FILE.exists():
        return set()

    try:
        payload = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()

    if isinstance(payload, list):
        return {str(item) for item in payload if item}
    if isinstance(payload, dict):
        return {str(item) for item in payload.get("urls", []) if item}
    return set()


def save_sent_urls(urls: set[str]) -> None:
    STATE_FILE.write_text(json.dumps(sorted(urls), ensure_ascii=False, indent=2), encoding="utf-8")


def get_new_jobs() -> list[dict]:
    jobs = search_jobs(
        keywords=DEFAULT_KEYWORDS,
        location=LOCATION,
        max_results=MAX_RESULTS,
    )

    sent_urls = load_sent_urls()
    new_jobs: list[dict] = []

    for job in jobs:
        url = (job.get("url") or "").strip()
        if not url or url in sent_urls:
            continue
        new_jobs.append(job)

    if new_jobs:
        updated_urls = sent_urls | {job.get("url", "").strip() for job in new_jobs if job.get("url")}
        save_sent_urls(updated_urls)

    return new_jobs


def run_scheduled_alerts() -> None:
    print(f"Bot iniciado. Intervalo: {INTERVAL_SECONDS} segundos | Local: {LOCATION}")

    while True:
        try:
            new_jobs = get_new_jobs()
            if new_jobs:
                message = build_telegram_message(new_jobs, f"estagio suporte ti em {LOCATION}")
                send_telegram_message(message)
                print(f"Mensagem enviada com {len(new_jobs)} vagas novas.")
            else:
                print("Nenhuma vaga nova encontrada no ciclo atual.")
        except Exception as exc:  # pragma: no cover
            print(f"Erro no ciclo: {exc}")

        time.sleep(INTERVAL_SECONDS)


def main() -> None:
    alerts_thread = threading.Thread(target=run_scheduled_alerts, daemon=True)
    alerts_thread.start()
    run_telegram_bot()


if __name__ == "__main__":
    main()
