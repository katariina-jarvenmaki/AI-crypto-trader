# modules/history_archiver/utils.py
# version 2.0, aug 2025

import os

def check_if_analysis_log_file_exists(full_path: str) -> bool:
    return os.path.exists(full_path)

def analysis_entries_loader(max_age_hours, history_log_path):

    from dateutil.parser import isoparse
    from datetime import datetime, timedelta
    from utils.get_timestamp import get_timestamp
    from utils.load_configs_and_logs import load_configs_and_logs
    from utils.load_entries_in_time_range import load_entries_in_time_range

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

def datetime_manager(mode=None):

    from dateutil.parser import isoparse
    from datetime import datetime, timedelta
    from utils.get_timestamp import get_timestamp

    # Daily
    timestamp = get_timestamp()
    now = isoparse(timestamp)
    current_day = now.strftime("%d-%m-%Y")

    yesterday_datetime = now - timedelta(days=1)
    yesterday = yesterday_datetime.strftime("%d-%m-%Y")

    # Weekly
    last_monday = now - timedelta(days=now.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)
    week = f"{last_monday.strftime('%d-%m-%Y')}_to_{last_sunday.strftime('%d-%m-%Y')}"
    week_dates = [(last_monday + timedelta(days=i)).strftime('%d-%m-%Y') for i in range(7)]
    this_week_start = last_sunday + timedelta(days=1)

    # Monthly
    first_day_this_month = now.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)
    last_month = first_day_last_month.strftime("%m-%Y")
    
    return {
        "timestamp": timestamp,
        "current_day": current_day,                
        "yesterday_datetime": yesterday_datetime.isoformat(),
        "yesterday": yesterday,
        "week": week,
        "week_dates": week_dates,
        "last_month": last_month,
        "last_monday": last_monday.isoformat(),
        "last_sunday": last_sunday.isoformat(),
        "this_week_start": this_week_start.isoformat(),
        "first_day_this_month": first_day_this_month.isoformat(),
        "last_day_last_month": last_day_last_month.isoformat(),
        "first_day_last_month": first_day_last_month.isoformat()
    }

def get_archive_log_paths(datetime_data):

    archive_log_path = "../AI-crypto-trader-logs/analysis_logs/history_archives/"
    extension = ".jsonl"

    history_analysis_log_name_base = "history_analyzer_log_"

    daily_log_name = f"{history_analysis_log_name_base}daily_{datetime_data['yesterday']}"
    weekly_log_name = f"{history_analysis_log_name_base}weekly_{datetime_data['week']}"
    monthly_log_name = f"{history_analysis_log_name_base}monthly_{datetime_data['last_month']}"

    daily_log_path = f"{archive_log_path}{daily_log_name}{extension}"
    weekly_log_path = f"{archive_log_path}{weekly_log_name}{extension}"
    monthly_log_path = f"{archive_log_path}{monthly_log_name}{extension}"

    return {
        "log_path": archive_log_path,
        "daily_log_name": daily_log_name,                
        "weekly_log_name": weekly_log_name,
        "monthly_log_name": monthly_log_name,
        "daily_log_path": daily_log_path,                
        "weekly_log_path": weekly_log_path,
        "monthly_log_path": monthly_log_path
    }