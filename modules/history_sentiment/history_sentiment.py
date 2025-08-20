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
from modules.save_and_validate.save_and_validate import save_and_validate
from modules.history_sentiment.trend_reversal import trend_reversal_analyzer

def sentiment_analyzer(all_symbols, history_config, history_entries, sentiment_entries, sentiment_log_path, sentiment_log_schema_path):

    print(f"\n💹 Running Sentiment Analyzer...")

    if isinstance(history_entries, dict):
        latest_values = list(chain.from_iterable(history_entries.values()))
    else:
        latest_values = history_entries

    bias_analysis_24h = compute_bias(latest_values, time_window_hours=24.0)
    bias_analysis_1h = compute_bias(latest_values, time_window_hours=1.0)
    if bias_analysis_24h is not None or bias_analysis_1h is not None:
        print(f"\n✅ Bias Analysis complete")
    else:
        print(f"\n❌ Bias Analysis failed")

    trend_analysis = trend_reversal_analyzer(bias_analysis_24h, bias_analysis_1h, sentiment_entries)

    combined_results = {
        "timestamp": get_timestamp(),
        "broad-sentiment": bias_analysis_24h,
        "hour-sentiment": bias_analysis_1h,
        "trend-reversal": trend_analysis
    }

    # Save results to log
    print(f"⏭  Result: {combined_results}")
    print(f"\n❇️  Saving new result to {sentiment_log_path}")
    save_and_validate(
        data=combined_results,
        path=sentiment_log_path,
        schema=sentiment_log_schema_path,
        verbose=False
    )

    print(f"✅ History Sentiment Analysis complete\n")

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

    now = isoparse(get_timestamp())
    oldest_allowed = (now - timedelta(hours=24)).isoformat()
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
    oldest_allowed = (now - timedelta(hours=24)).isoformat()
    newest_allowed = now.isoformat()

    sentiment_entries = load_entries_in_time_range(
        file_path=sentiment_log_path,
        symbols=all_symbols,
        start_time=oldest_allowed,
        end_time=newest_allowed
    )

    sentiment_data = sentiment_analyzer(all_symbols, history_config, history_entries, sentiment_entries, sentiment_log_path, sentiment_log_schema_path)
    # print(f"\nSentiment_data: {sentiment_data}")
        