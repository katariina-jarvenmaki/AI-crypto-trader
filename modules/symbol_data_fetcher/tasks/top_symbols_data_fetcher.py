# modules/symbol_data_fetcher/tasks/top_symbols_data_fetcher.py

from datetime import datetime

from modules.symbol_data_fetcher.symbol_data_fetcher_config import (
    LOCAL_TIMEZONE,
    TOP_SYMBOL_FETCH_COOLDOWN_MINUTES,
    TOP_APPEND_RETRY_DELAY_SECONDS,
    TEMP_LOG_TOP_SYMBOLS,
)
from modules.symbol_data_fetcher.utils import fetch_symbols_data

def run_top_symbols_data_fetcher():

    print(f"🕒 Running fetch at: {datetime.now(LOCAL_TIMEZONE)}")
    
    fetch_symbols_data(
        SYMBOL_KEYS=["potential_to_long", "potential_to_short"],
        TEMP_SYMBOLS_LOG=TEMP_LOG_TOP_SYMBOLS,
        SYMBOL_FETCH_COOLDOWN_MINUTES=TOP_SYMBOL_FETCH_COOLDOWN_MINUTES,
        APPEND_RETRY_DELAY_SECONDS=TOP_APPEND_RETRY_DELAY_SECONDS
    )

def main():
    run_top_symbols_data_fetcher()


if __name__ == "__main__":
    main()
