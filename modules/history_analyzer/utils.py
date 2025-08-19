# modules/history_analyzer/utils.py
# version 2.0, aug 2025

from utils.load_configs_and_logs import load_configs_and_logs
from utils.load_latest_entries_per_symbol import load_latest_entries_per_symbol

def get_data_from_logs(symbols):

    configs_and_logs = load_configs_and_logs([
        {
            "name": "history",
            "mid_folder": "analysis",
            "module_key": "history_analyzer",
            "extension": ".jsonl",
            "return": ["full_log_path", "full_log_schema_path"]
        }
    ])

    log_path = configs_and_logs.get("history_full_log_path")
    log_schema_path = configs_and_logs.get("history_full_log_schema_path")

    latest_entries = load_latest_entries_per_symbol(symbols, log_path, limit=1, max_age_minutes=1440)

    return latest_entries, log_path, log_schema_path