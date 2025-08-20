# modules/history_analyzer/utils.py
# version 2.0, aug 2025

from utils.load_latest_entry import load_latest_entry
from utils.load_configs_and_logs import load_configs_and_logs
from utils.load_latest_entries_per_symbol import load_latest_entries_per_symbol

def get_data_from_logs(symbols, history_config: dict):

    config = history_config.get("history_analyzer")
    configs_and_logs_settings = config.get("configs_and_logs", [])
    min_age_minutes = config.get("min_age_minutes", 5)
    max_age_minutes = config.get("max_age_minutes", 1440)

    configs_and_logs = load_configs_and_logs(configs_and_logs_settings)

    log_path = configs_and_logs.get("history_full_log_path")
    log_schema_path = configs_and_logs.get("history_full_log_schema_path")

    latest_entry = load_latest_entry(
        file_path=log_path,
        limit=1,
        use_timestamp=True,
    )
    latest_analysis_timestamp = latest_entry[0]["timestamp"] if latest_entry else None

    analysis_data = load_latest_entries_per_symbol(
        symbols,
        log_path,
        limit=1,
        min_age_minutes=min_age_minutes,
        max_age_minutes=max_age_minutes,
    )

    return analysis_data, latest_analysis_timestamp, log_path, log_schema_path