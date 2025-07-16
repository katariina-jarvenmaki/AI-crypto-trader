# modules/history_analyzer/history_analyzer.py

from pprint import pprint
from modules.history_analyzer.config_history_analyzer import CONFIG
from modules.history_analyzer.data_collector import data_collector
from modules.history_analyzer.history_log_processor import history_log_processor
from modules.history_analyzer.history_archiver import history_archiver
from modules.history_analyzer.analysis_engine import analysis_engine
from modules.history_analyzer.utils import get_latest_symbols_from_log
from modules.history_analyzer.analysis_log_processor import analysis_log_processor

def main():
    
    # Archive previous logs
    history_archiver()

    # Get the symbols
    symbols = get_latest_symbols_from_log(CONFIG["symbol_log_path"])
    if not symbols:
        print("No symbols found in latest symbol log.")
        return

    print(f"Found {len(symbols)} symbols to process...")

    # Running data_collector
    parsed_entries = data_collector(symbols)

    # Running history_log_processor
    history_log_processor(parsed_entries)

    # Running analysis_engine
    analysis_results = analysis_engine(symbols)

    # Archive previous logs
    analysis_log_processor(parsed_entries, analysis_results)

if __name__ == "__main__":
    main()