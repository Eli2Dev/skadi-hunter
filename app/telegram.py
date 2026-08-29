from __future__ import annotations

import os
from typing import Any

import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def build_telegram_message(jobs: list[dict[str, Any]], keyword: str) -> str:
    if not jobs:
        return (
            "📢 Alertas de vagas\n"
            f"Busca: {keyword}\n"
            "\n"
            "Nenhuma oportunidade encontrada no momento para esse filtro."
        )

    lines = [
        "📢 ALERTA DE VAGAS - SALVADOR",
        f"Busca: {keyword}",
        f"Total: {len(jobs)}",
        "",
    ]

    for index, job in enumerate(jobs, start=1):
        title = (job.get("title") or "Sem título").strip()
        url = (job.get("url") or "Sem link").strip()
        summary = (job.get("summary") or job.get("body") or "Sem descrição").strip()
        source = (job.get("source") or "Fonte desconhecida").strip()

        lines.append(f"{index}. {title}")
        lines.append(f"🔗 {url}")
        lines.append(f"📝 {summary[:200]}")
        lines.append(f"🏷️ {source}")
        lines.append("")

    lines.append("✅ Dica: revise os links e aplique em todas as vagas compatíveis com estágio em suporte de TI.")
    return "\n".join(lines).strip()


def send_telegram_message(message: str, token: str | None = None, chat_id: str | None = None) -> bool:
    token = token or TELEGRAM_TOKEN
    chat_id = chat_id or TELEGRAM_CHAT_ID

    if not token or not chat_id:
        raise ValueError("Defina TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID antes de enviar o alerta.")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    response = requests.post(url, data=payload, timeout=20)
    response.raise_for_status()
    return response.json().get("ok", False)
