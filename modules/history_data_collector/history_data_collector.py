import json
from typing import List
from utils.get_timestamp import get_timestamp
from utils.get_symbols_to_use import get_symbols_to_use
from utils.load_configs_and_logs import load_configs_and_logs
from utils.load_latest_entries_per_symbol import load_latest_entries_per_symbol

def data_from_logs(symbols: List[str]):

    configs_and_logs = load_configs_and_logs([
        {
            "name": "collector",
            "mid_folder": "analysis",
            "module_key": "history_data_collector",
            "extension": ".jsonl",
            "return": ["full_temp_log_path"]
        },
        {
            "name": "ohlcv",
            "mid_folder": "fetch",
            "module_key": "multi_interval_ohlcv",
            "extension": ".jsonl",
            "return": ["full_log_path"]
        },
        {
            "name": "price",
            "mid_folder": "fetch",
            "module_key": "price_data_fetcher",
            "extension": ".jsonl",
            "return": ["full_log_path"]
        }
    ])

    latest_collection = load_latest_entries_per_symbol(
        symbols=symbols,
        file_path=configs_and_logs["collector_full_temp_log_path"],
        max_age_minutes=1440  # esim. 24 tuntia
    )

    latest_ohlcv = load_latest_entries_per_symbol(
        symbols=symbols,
        file_path=configs_and_logs["ohlcv_full_log_path"],
        max_age_minutes=1440
    )

    latest_price = load_latest_entries_per_symbol(
        symbols=symbols,
        file_path=configs_and_logs["price_full_log_path"],
        max_age_minutes=1440
    )

    return latest_collection, latest_ohlcv, latest_price

def history_data_collector(symbols: List[str]):

    collector_logs, ohlcv_logs, price_logs = data_from_logs(symbols)

    print("Collector logs:", collector_logs)
    # print("OHLCV logs:", ohlcv_logs)
    # print("Price logs:", price_logs)

if __name__ == "__main__":
    
    configs_and_logs = load_configs_and_logs([
        {
            "name": "symbol",
            "mid_folder": "analysis",
            "module_key": "symbol_data_fetcher",
            "extension": ".jsonl",
            "return": ["config", "full_log_path", "full_log_schema_path"]
        }
    ])

    # Vastaa alkuperäisen koodin muuttujia
    module_log_path = configs_and_logs["symbol_full_log_path"]
    module_config = configs_and_logs["symbol_config"]

    result = get_symbols_to_use(module_config, module_log_path)
    all_symbols = result["all_symbols"]

    history_data_collector(all_symbols)
