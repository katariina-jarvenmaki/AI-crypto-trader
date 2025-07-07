# modules/symbol_data_fetcher/tasks/top_symbols_data_fetcher.py

from datetime import datetime

from modules.symbol_data_fetcher.config_symbol_data_fetcher import (
    LOCAL_TIMEZONE,
    TASK_CONFIG,
)
from modules.symbol_data_fetcher.utils import fetch_symbols_data


def run_top_symbols_data_fetcher():
    print(f"🕒 Running fetch at: {datetime.now(LOCAL_TIMEZONE)}")

    task_settings = TASK_CONFIG["top"]

    fetch_symbols_data(
        SYMBOL_KEYS=task_settings["symbol_keys"],
        TEMP_SYMBOLS_LOG=task_settings["temp_log"],
        SYMBOL_FETCH_COOLDOWN_MINUTES=task_settings["cooldown_minutes"],
        APPEND_RETRY_DELAY_SECONDS=task_settings["retry_delay"]
    )


def main():
    run_top_symbols_data_fetcher()


if __name__ == "__main__":
    main()
