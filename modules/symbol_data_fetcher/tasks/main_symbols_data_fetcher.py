# modules/symbol_data_fetcher/tasks/main_symbols_data_fetcher.py

from datetime import datetime

from modules.symbol_data_fetcher.symbol_data_fetcher_config import (
    LOCAL_TIMEZONE,
    MAIN_SYMBOL_FETCH_COOLDOWN_MINUTES,
    MAIN_APPEND_RETRY_DELAY_SECONDS,
    TEMP_LOG_MAIN_SYMBOLS,
)
from modules.symbol_data_fetcher.utils import fetch_symbols_data

def run_main_symbols_data_fetcher():

    print(f"🕒 Running fetch at: {datetime.now(LOCAL_TIMEZONE)}")
    
    fetch_symbols_data(
        SYMBOL_KEYS=["potential_both_ways"],
        TEMP_SYMBOLS_LOG=TEMP_LOG_MAIN_SYMBOLS,
        SYMBOL_FETCH_COOLDOWN_MINUTES=MAIN_SYMBOL_FETCH_COOLDOWN_MINUTES,
        APPEND_RETRY_DELAY_SECONDS=MAIN_APPEND_RETRY_DELAY_SECONDS
    )

def main():
    run_main_symbols_data_fetcher()

if __name__ == "__main__":
    main()