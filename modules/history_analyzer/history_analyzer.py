# modules/history_analyzer/history_analyzer.py
# version 2.0, aug 2025

from utils.get_symbols_to_use import get_symbols_to_use
from utils.load_configs_and_logs import load_configs_and_logs
from modules.history_analyzer.utils import get_data_from_logs
from modules.history_analyzer.analysis_engine import analysis_engine
from modules.save_and_validate.save_and_validate import save_and_validate
from utils.load_latest_entries_per_symbol import load_latest_entries_per_symbol

def history_analyzer(symbols, history_config, data_collection):

    print(f"\n💡 Found {len(symbols)} symbols to process...")

    analysis_data, latest_analysis_timestamp, log_path, log_schema_path = get_data_from_logs(symbols) or ({}, None, None)
    all_analysis_data = []

    for symbol in symbols:

        print(f"\n⚙️  Symbol: {symbol}")

        collection_entry = data_collection.get(symbol, {})
        analysis_entry = analysis_data.get(symbol, {})

        col_ts = collection_entry.get("timestamp") if collection_entry else None
        anl_ts = latest_analysis_timestamp

        if (
            col_ts is not None
            and (
                anl_ts is None
                or col_ts > anl_ts
            )
        ):
            print(f"💹 Continuing the process for the symbol {symbol}")

            result = analysis_engine(
                symbol, history_config, collection_entry, analysis_entry
            )
            all_analysis_data.append(result)

        else:
            print(f"⏭  Skipping {symbol} — data is up-to-date or missing required collection timestamps")

    # Save results to log
    print(f"\n❇️  Saving new result to {log_path}\n")
    save_and_validate(
        data=all_analysis_data,
        path=log_path,
        schema=log_schema_path,
        verbose=False
    )

    return all_analysis_data

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
