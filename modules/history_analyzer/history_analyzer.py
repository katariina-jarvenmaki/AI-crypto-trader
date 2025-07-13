# modules/history_analyzer/history_analyzer.py

from pprint import pprint
from modules.history_analyzer.config_history_analyzer import CONFIG
from modules.history_analyzer.data_collector import process_latest_entries_for_symbols
from modules.history_analyzer.utils import get_latest_symbols_from_log
from modules.history_analyzer.data_collector import process_latest_entries_for_symbols

def main():
    
    symbols = get_latest_symbols_from_log(CONFIG["symbol_log_path"])
    if not symbols:
        print("No symbols found in latest symbol log.")
        return

    print(f"Found {len(symbols)} symbols to process...")
    parsed_entries = process_latest_entries_for_symbols(symbols)

    for entry in parsed_entries:
        pprint(entry)

if __name__ == "__main__":
    main()