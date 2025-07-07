# modules/symbol_data_fetcher/tasks/main_symbols_data_fetcher.py

from modules.core.utils.logger import log
from modules.symbol_data_fetcher.config_symbol_data_fetcher import TASK_CONFIG
from modules.symbol_data_fetcher.utils import fetch_symbols_data

def run_main_symbols_data_fetcher():
    log("Running main_symbols_data_fetcher...")

    config = TASK_CONFIG["main"]

    fetch_symbols_data(
        SYMBOL_KEYS=config["symbol_keys"],
        TEMP_SYMBOLS_LOG=config["temp_log"],
        SYMBOL_FETCH_COOLDOWN_MINUTES=config["cooldown_minutes"],
        APPEND_RETRY_DELAY_SECONDS=config["retry_delay"],
    )

def main():
    run_main_symbols_data_fetcher()

if __name__ == "__main__":
    main()
