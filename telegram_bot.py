from __future__ import annotations

import os

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


def main() -> None:
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN não definido.")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("vagas", vagas))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help_command))
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
