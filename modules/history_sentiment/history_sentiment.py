# modules/history_sentiment/history_sentiment.py
# version 2.0, aug 2025

from itertools import chain
from dateutil.parser import isoparse
from datetime import datetime, timedelta
from utils.get_timestamp import get_timestamp
from modules.history_sentiment.compute_bias import compute_bias
from utils.get_symbols_to_use import get_symbols_to_use
from utils.load_configs_and_logs import load_configs_and_logs
from utils.load_entries_in_time_range import load_entries_in_time_range

def sentiment_analyzer(all_symbols, history_config, log_entries):

    print(f"\nRunning Sentiment Analyzer...")

    if isinstance(log_entries, dict):
        latest_values = list(chain.from_iterable(log_entries.values()))
    else:
        latest_values = log_entries

    bias_analysis_24h = compute_bias(latest_values, time_window_hours=24.0)
    bias_analysis_1h = compute_bias(latest_values, time_window_hours=1.0)

    trend_reversal_analyzer(bias_analysis_24h, bias_analysis_1h, log_entries)

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

    now = isoparse(get_timestamp())
    oldest_allowed = (now - timedelta(hours=24)).isoformat()
    newest_allowed = now.isoformat()

    log_entries = load_entries_in_time_range(
        file_path=log_path,
        symbols=all_symbols,
        start_time=oldest_allowed,
        end_time=newest_allowed
    )

    sentiment_data = sentiment_analyzer(all_symbols, history_config, log_entries)
    # print(f"\nSentiment_data: {sentiment_data}")