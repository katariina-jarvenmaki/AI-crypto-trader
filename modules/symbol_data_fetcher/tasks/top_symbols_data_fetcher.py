# modules/symbol_data_fetcher/tasks/top_symbols_data_fetcher.py

from datetime import datetime

from modules.symbol_data_fetcher.config_symbol_data_fetcher import (
    LOCAL_TIMEZONE,
    TASK_CONFIG,
)
from modules.symbol_data_fetcher.utils import fetch_symbols_data


def run_top_symbols_data_fetcher():

    print(f"🕒 Running fetch at: {datetime.now(LOCAL_TIMEZONE)}")

    config = TASK_CONFIG["top"]

    fetch_symbols_data({
        "symbol_keys": config["symbol_keys"], 
        "temp_log": config["temp_log"],
        "cooldown_minutes": config["cooldown_minutes"],
        "retry_delay": config["retry_delay"],
    })

def main():
    run_top_symbols_data_fetcher()


if __name__ == "__main__":
    main()
