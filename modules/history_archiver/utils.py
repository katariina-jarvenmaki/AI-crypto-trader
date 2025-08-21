# modules/history_archiver/utils.py
# version 2.0, aug 2025

from dateutil.parser import isoparse
from datetime import datetime, timedelta
from utils.get_timestamp import get_timestamp
from utils.load_configs_and_logs import load_configs_and_logs
from utils.load_entries_in_time_range import load_entries_in_time_range

def analysis_entries_loader(max_age_hours, history_log_path):

    now = isoparse(get_timestamp())
    newest_allowed = now.isoformat()
    oldest_allowed = (now - timedelta(hours=max_age_hours)).isoformat()

    # Load current log entries
    analysis_entries = load_entries_in_time_range(
        file_path=history_log_path,
        start_time=oldest_allowed,
        end_time=newest_allowed
    )

    return analysis_entries
