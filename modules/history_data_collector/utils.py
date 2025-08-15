# modules/history_data_collector/utils.py
# version 2.0, aug 2025

from typing import List
from utils.load_configs_and_logs import load_configs_and_logs
from utils.load_latest_entries_per_symbol import load_latest_entries_per_symbol

def get_data_from_logs(symbols: List[str]):

    configs_and_logs = load_configs_and_logs([
        {
            "name": "collector",
            "mid_folder": "analysis",
            "module_key": "history_data_collector",
            "extension": ".jsonl",
            "return": ["full_temp_log_path", "full_log_schema_path"]
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

    log_path=configs_and_logs["collector_full_temp_log_path"]
    log_schema_path=configs_and_logs["collector_full_log_schema_path"]

    return latest_collection, latest_ohlcv, latest_price, log_path, log_schema_path
