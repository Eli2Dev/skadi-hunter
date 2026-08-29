from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def get_greeting_for_time() -> str:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "bom dia"
    if 12 <= hour < 18:
        return "boa tarde"
    return "boa noite"


def build_intro_message(user_name: str = "Eli") -> str:
    greeting = get_greeting_for_time()
    greeting = greeting[0].upper() + greeting[1:]
    lines = [
        "✦ Skadi Hunter ✦",
        f"{greeting}, {user_name}!",
        "",
        "Sou a Skadi, sua assistente de vagas em Salvador.",
        "Eu cuido dos alertas mais relevantes para você.",
        "",
        "Serviços disponíveis:",
        "• Vagas de estágio em suporte de TI",
        "• Help desk e Suporte técnico",
        "• Vagas correlatas em Salvador",
        "• Alertas automáticos em intervalos regulares",
        "",
        "Use /vagas para receber o próximo alerta.",
        "Use /status para ver o estado do serviço.",
    ]
    return "\n".join(lines).strip()


def build_help_message() -> str:
    return (
        "✦ Comandos disponíveis ✦\n"
        "\n"
        "/start — apresentação inicial\n"
        "/vagas — busca as vagas mais recentes\n"
        "/status — mostra o estado do serviço\n"
        "/help — mostra esta ajuda"
    )


def build_status_message(status: str = "online", location: str = "Salvador") -> str:
    return (
        "✦ Status do serviço ✦\n"
        f"Status: {status}\n"
        f"Local: {location}\n"
        "Foco: estágio em suporte de TI e áreas correlatas\n"
        "Próximo ciclo: a cada 5 horas"
    )


def build_telegram_message(jobs: list[dict[str, Any]], keyword: str) -> str:
    if not jobs:
        return (
            "📢 Alertas de vagas\n"
            f"Busca: {keyword}\n"
            "\n"
            "Nenhuma oportunidade encontrada no momento para esse filtro."
        )

    lines = [
        "✦ Skadi Hunter ✦",
        f"📍 {keyword} · Salvador",
        f"✨ {len(jobs)} oportunidades em destaque",
        "",
    ]

    for index, job in enumerate(jobs, start=1):
        title = (job.get("title") or "Sem título").strip()
        url = (job.get("url") or "Sem link").strip()
        summary = (job.get("summary") or job.get("body") or "Sem descrição").strip()
        source = (job.get("source") or "Fonte desconhecida").strip()

        lines.append(f"{index}. {title}")
        lines.append(f"🔗 {url}")
        if summary:
            lines.append(f"🧭 {summary[:120]}")
        lines.append(f"🏛 {source}")
        lines.append("·" * 24)
        lines.append("")

    lines.append("⚡ Revisar e aplicar nas que mais combinam com estágio em suporte de TI.")
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
