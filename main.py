from __future__ import annotations

import threading

from bot_loop import run_scheduled_alerts
from telegram_bot import main as run_telegram_bot


def main() -> None:
    alerts_thread = threading.Thread(target=run_scheduled_alerts, daemon=True)
    alerts_thread.start()
    run_telegram_bot()


if __name__ == "__main__":
    main()
