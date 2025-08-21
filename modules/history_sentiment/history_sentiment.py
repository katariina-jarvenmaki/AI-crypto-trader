# modules/history_sentiment/history_sentiment.py
# version 2.0, aug 2025

from itertools import chain
from dateutil.parser import isoparse
from datetime import datetime, timedelta
from utils.get_timestamp import get_timestamp
from utils.get_symbols_to_use import get_symbols_to_use
from utils.load_configs_and_logs import load_configs_and_logs
from modules.history_sentiment.compute_bias import compute_bias
from utils.load_entries_in_time_range import load_entries_in_time_range
# from modules.save_and_validate.save_and_validate import save_and_validate
# from modules.history_sentiment.trend_reversal import trend_reversal_analyzer

def sentiment_analyzer(all_symbols, history_config, history_entries, sentiment_entries, sentiment_log_path, sentiment_log_schema_path):

    print(f"\n💹 Running Sentiment Analyzer...")

    sentiment_config = history_config['history_sentiment']

    if isinstance(history_entries, dict):
        latest_values = list(chain.from_iterable(history_entries.values()))
    else:
        latest_values = history_entries

    bias_results = {}
    bias_time_windows_hours = sentiment_config['main']['bias_time_windows_hours']
    result_keys = sentiment_config['main']['result_keys']
    for window in bias_time_windows_hours:
        result = compute_bias(latest_values, sentiment_config, time_window_hours=window)
        # print(f"\n{result}")


#         key_name = result_keys.get(str(window), f"bias_{window}h")
#         bias_results[key_name] = result

#     if any(v is not None for v in bias_results.values()):
#         print(f"\n✅ Bias Analysis complete")
#     else:
#         print(f"\n❌ Bias Analysis failed")

#     trend_reversal_config = sentiment_config['trend_reversal']
#     trend_analysis = trend_reversal_analyzer(
#         bias_results,
#         sentiment_entries,
#         trend_reversal_config
#     )
#     bias_results[result_keys.get("trend", "trend_shift")] = trend_analysis

#     combined_results = {"timestamp": get_timestamp(), **bias_results}

    # Save results to log
#     print(f"⏭  Result: {combined_results}")
#     print(f"\n❇️  Saving new result to {sentiment_log_path}")
#     save_and_validate(
#         data=combined_results,
#         path=sentiment_log_path,
#         schema=sentiment_log_schema_path,
#         verbose=False
#     )

#     print(f"✅ History Sentiment Analysis complete\n")
#     return combined_results

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
        },
        {
            "name": "sentiment",
            "mid_folder": "analysis",
            "module_key": "history_sentiment",
            "extension": ".jsonl",
            "return": ["full_log_path", "full_log_schema_path"]
        }
    ])

    symbol_log_path = configs_and_logs["symbol_full_log_path"]
    symbol_config = configs_and_logs["symbol_config"]

    result = get_symbols_to_use(symbol_config, symbol_log_path)
    all_symbols = result["all_symbols"]

    history_config = configs_and_logs["history_config"]
    history_log_path = configs_and_logs.get("history_full_log_path")

    max_age_hours = history_config["history_sentiment"]["main"]["max_age_hours"]

    now = isoparse(get_timestamp())
    oldest_allowed = (now - timedelta(hours=max_age_hours)).isoformat()
    newest_allowed = now.isoformat()

    history_entries = load_entries_in_time_range(
        file_path=history_log_path,
        symbols=all_symbols,
        start_time=oldest_allowed,
        end_time=newest_allowed
    )

    sentiment_log_path = configs_and_logs.get("sentiment_full_log_path")
    sentiment_log_schema_path = configs_and_logs.get("sentiment_full_log_schema_path")

    now = isoparse(get_timestamp())
    oldest_allowed = (now - timedelta(hours=max_age_hours)).isoformat()
    newest_allowed = now.isoformat()

    sentiment_entries = load_entries_in_time_range(
        file_path=sentiment_log_path,
        start_time=oldest_allowed,
        end_time=newest_allowed
    )

    sentiment_data = sentiment_analyzer(all_symbols, history_config, history_entries, sentiment_entries, sentiment_log_path, sentiment_log_schema_path)
    # print(f"\nSentiment_data: {sentiment_data}")
        