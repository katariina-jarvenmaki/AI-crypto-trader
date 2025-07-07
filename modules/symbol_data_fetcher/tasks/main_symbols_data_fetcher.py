# modules/symbol_data_fetcher/tasks/main_symbols_data_fetcher.py

from modules.symbol_data_fetcher.config_symbol_data_fetcher import TASK_CONFIG
from modules.symbol_data_fetcher.utils import fetch_symbols_data

def run_main_symbols_data_fetcher():
    
    print("Running main_symbols_data_fetcher...")

    config = TASK_CONFIG["main"]

    fetch_symbols_data({
        "symbol_keys": config["symbol_keys"], 
        "temp_log": config["temp_log"],
        "cooldown_minutes": config["cooldown_minutes"],
        "retry_delay": config["retry_delay"],
    })

def main():
    run_main_symbols_data_fetcher()

if __name__ == "__main__":
    main()
