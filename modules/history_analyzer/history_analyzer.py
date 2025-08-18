# modules/history_analyzer/history_analyzer.py
# version 2.0, aug 2025

from utils.get_symbols_to_use import get_symbols_to_use
from utils.load_configs_and_logs import load_configs_and_logs
from modules.history_analyzer.utils import get_data_from_logs
from utils.load_latest_entries_per_symbol import load_latest_entries_per_symbol

def history_analyzer(symbols, history_config, data_collection):

    print(f"\n💡 Found {len(symbols)} symbols to process...")

    if not data_collection:
        latest_entries, log_path, log_schema_path = get_data_from_logs(symbols, history_config)
        print("⚡ data_collection was empty, fetched latest_entries from logs")
    else:
        _, log_path, log_schema_path = get_data_from_logs(symbols)
        latest_entries = data_collection
        print("✅ Using provided data_collection")

    # print(f"all_symbols: {symbols}")
    # print(f"history_config: {history_config}")
    # print(f"latest_entries: {latest_entries}")
    # print(f"log_path: {log_path}")
    # print(f"log_schema_path: {log_schema_path}")

if __name__ == "__main__":

    print(f"\nRunning History Analyzer...\n")

    configs_and_logs = load_configs_and_logs([
        {
            "name": "symbol",
            "mid_folder": "analysis",
            "module_key": "symbol_data_fetcher",
            "extension": ".jsonl",
            "return": ["config", "full_log_path"]
        },
        {
            "name": "history",
            "mid_folder": "analysis",
            "module_key": "history_analyzer",
            "extension": ".json",
            "return": ["config"]
        },
        {
            "name": "collector",
            "mid_folder": "analysis",
            "module_key": "history_data_collector",
            "extension": ".jsonl",
            "return": ["full_temp_log_path", "full_log_schema_path"],
        }
    ])

    symbol_log_path = configs_and_logs["symbol_full_log_path"]
    symbol_config = configs_and_logs["symbol_config"]

    result = get_symbols_to_use(symbol_config, symbol_log_path)
    all_symbols = result["all_symbols"]

    history_config = configs_and_logs["history_config"]
    temporary_path = configs_and_logs.get("collector_full_temp_log_path")
    latest_entries = load_latest_entries_per_symbol(all_symbols, temporary_path, max_age_minutes=1440)

    history_analyzer(all_symbols, history_config, latest_entries)
