# modules/history_analyzer/history_analyzer.py

from pprint import pprint
from modules.history_analyzer.config_history_analyzer import CONFIG
from modules.history_analyzer.data_collector import data_collector
from modules.history_analyzer.history_log_processor import history_log_processor
from modules.history_analyzer.utils import get_latest_symbols_from_log

def main():
    
    symbols = get_latest_symbols_from_log(CONFIG["symbol_log_path"])
    if not symbols:
        print("No symbols found in latest symbol log.")
        return

    print(f"Found {len(symbols)} symbols to process...")

    # Running data_collector
    parsed_entries = data_collector(symbols)

    # Running history_log_processor
    history_log_processor(parsed_entries)

if __name__ == "__main__":
    main()