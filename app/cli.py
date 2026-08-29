from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from app.search import search_jobs
from app.telegram import build_telegram_message, send_telegram_message


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Busca vagas de estágio em suporte de TI e áreas correlatas.")
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=["estagio suporte ti", "help desk", "suporte tecnico"],
        help="Palavras-chave para a busca, ex.: estagio suporte ti help desk",
    )
    parser.add_argument("--location", default="Salvador", help="Localidade da vaga, ex.: Salvador, Bahia, remoto")
    parser.add_argument("--max-results", type=int, default=10, help="Quantidade máxima de vagas para retornar")
    parser.add_argument("--output", default="vagas.json", help="Arquivo JSON para salvar os resultados")
    parser.add_argument("--send-telegram", action="store_true", help="Envie as vagas para o Telegram")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    jobs = search_jobs(
        keywords=args.keywords,
        location=args.location,
        max_results=args.max_results,
    )

    output_path = Path(args.output)
    output_path.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Encontradas {len(jobs)} vagas.")
    for job in jobs:
        print(f"- {job['title']} | {job['url']}")

    if args.send_telegram:
        keyword_text = " ".join(args.keywords)
        message = build_telegram_message(jobs, keyword_text)
        try:
            sent = send_telegram_message(message)
            if sent:
                print("Mensagem enviada para o Telegram com sucesso.")
            else:
                print("Não foi possível enviar a mensagem por Telegram.")
        except ValueError as exc:
            print(f"Erro de configuração: {exc}")
        except Exception as exc:  # pragma: no cover
            print(f"Erro ao enviar mensagem: {exc}")


if __name__ == "__main__":
    main()
