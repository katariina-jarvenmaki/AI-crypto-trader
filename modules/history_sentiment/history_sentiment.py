# modules/history_sentiment/history_sentiment.py
# version 2.0, aug 2025

from utils.get_symbols_to_use import get_symbols_to_use
from utils.load_configs_and_logs import load_configs_and_logs
from utils.load_latest_entries_per_symbol import load_latest_entries_per_symbol

def sentiment_analyzer(all_symbols, history_config, latest_entries):

    print(f"\nRunning Sentiment Analyzer...")
    # print(f"all_symbols:    {all_symbols}")
    # print(f"history_config: {history_config}")
    # print(f"latest_entries: {latest_entries}")

if __name__ == "__main__":

    print(f"\nRunning History Sentiment...\n")

    configs_and_logs = load_configs_and_logs([
        {
            "name": "symbol",
            "mid_folder": "analysis",
            "module_key": "symbol_data_fetcher",
            "extension": ".jsonl",
            "return": ["config", "full_log_path", "full_log_schema_path"]
        },
        {
            "name": "history",
            "mid_folder": "analysis",
            "module_key": "history_analyzer",
            "extension": ".jsonl",
            "return": ["config", "full_log_path", "full_log_schema_path"]
        }
    ])

    symbol_log_path = configs_and_logs["symbol_full_log_path"]
    symbol_config = configs_and_logs["symbol_config"]

    result = get_symbols_to_use(symbol_config, symbol_log_path)
    all_symbols = result["all_symbols"]

    history_config = configs_and_logs["history_config"]
    log_path = configs_and_logs.get("history_full_log_path")

    latest_entries = load_latest_entries_per_symbol(all_symbols, log_path, max_age_minutes=1440)

    sentiment_data = sentiment_analyzer(all_symbols, history_config, latest_entries)
    # print(f"\nSentiment_data: {sentiment_data}")

