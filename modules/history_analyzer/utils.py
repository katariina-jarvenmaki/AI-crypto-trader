# modules/history_analyzer/utils.py
# version 2.0, aug 2025

from utils.load_latest_entry import load_latest_entry
from utils.load_configs_and_logs import load_configs_and_logs
from utils.load_latest_entries_per_symbol import load_latest_entries_per_symbol

MIN_AGE_MINUTES = 5

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

    latest_entry = load_latest_entry(
        file_path=log_path,
        limit=1,
        use_timestamp=True,
    )
    latest_analysis_timestamp = latest_entry[0]["timestamp"]

    analysis_data = load_latest_entries_per_symbol(symbols, log_path, limit=1, min_age_minutes=MIN_AGE_MINUTES, max_age_minutes=1440)

    return analysis_data, latest_analysis_timestamp, log_path, log_schema_path