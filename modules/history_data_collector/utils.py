# modules/history_data_collector/utils.py
# version 2.0, aug 2025

from typing import List
from utils.load_configs_and_logs import load_configs_and_logs
from utils.load_latest_entries_per_symbol import load_latest_entries_per_symbol

def get_data_from_logs(symbols: List[str], history_config):

    configs_and_logs_config = history_config.get("history_data_collector", {}).get("configs_and_logs", [])
    load_params = [
        {
            "name": conf.get("name"),
            "mid_folder": conf.get("mid_folder"),
            "module_key": conf.get("module_key"),
            "extension": conf.get("extension"),
            "return": conf.get("return", [])
        }
        for conf in configs_and_logs_config
    ]
    configs_and_logs = load_configs_and_logs(load_params)

    latest_entries = {}
    for conf in configs_and_logs_config:
        key = conf.get("key")
        file_path_key = f"{key}_{'full_temp_log_path' if key == 'collector' else 'full_log_path'}"
        max_age = conf.get("max_age_minutes", 1440)

        latest_entries[key] = load_latest_entries_per_symbol(
            symbols=symbols,
            file_path=configs_and_logs[file_path_key],
            max_age_minutes=max_age
        )

    latest_collection = latest_entries.get("collector")
    latest_ohlcv = latest_entries.get("ohlcv")
    latest_price = latest_entries.get("price")

    log_path = configs_and_logs.get("collector_full_temp_log_path")
    log_schema_path = configs_and_logs.get("collector_full_log_schema_path")

    return latest_collection, latest_ohlcv, latest_price, log_path, log_schema_path
