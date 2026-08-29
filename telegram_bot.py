from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.search import search_jobs
from app.telegram import (
    build_help_message,
    build_intro_message,
    build_status_message,
    build_telegram_message,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
LOCATION = os.getenv("JOB_LOCATION", "Salvador")
LOCK_PATH = Path(tempfile.gettempdir()) / "skadi_hunter_telegram.lock"


def fetch_vagas() -> str:
    jobs = search_jobs(
        keywords=["estagio suporte ti", "help desk", "suporte tecnico", "analista de suporte"],
        location=LOCATION,
        max_results=5,
    )
    if not jobs:
        return "Nenhuma vaga nova encontrada no momento."
    return build_telegram_message(jobs, f"estagio suporte ti em {LOCATION}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    name = user.first_name if user and user.first_name else "Eli"
    await update.message.reply_text(build_intro_message(name))


async def vagas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(fetch_vagas())


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(build_status_message("online", LOCATION))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(build_help_message())


def ensure_event_loop() -> asyncio.AbstractEventLoop:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def acquire_singleton_lock() -> bool:
    try:
        import fcntl
    except ImportError:
        return True

    try:
        fd = open(LOCK_PATH, "w", encoding="utf-8")
        fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except BlockingIOError:
        print("Telegram já está em execução em outra instância. Abortando polling duplicado.")
        return False


def release_singleton_lock() -> None:
    try:
        import fcntl
    except ImportError:
        return

    try:
        if LOCK_PATH.exists():
            with open(LOCK_PATH, "r+", encoding="utf-8") as lock_file:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass


def main() -> None:
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN não definido.")

    if not acquire_singleton_lock():
        return

    try:
        ensure_event_loop()

        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("vagas", vagas))
        app.add_handler(CommandHandler("status", status))
        app.add_handler(CommandHandler("help", help_command))
        app.run_polling(drop_pending_updates=True)
    finally:
        release_singleton_lock()


if __name__ == "__main__":
    main()
