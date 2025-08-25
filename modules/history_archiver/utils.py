# modules/history_archiver/utils.py
# version 2.0, aug 2025

import os

def check_if_analysis_log_file_exists(full_path: str) -> bool:
    return os.path.exists(full_path)

def analysis_entries_loader(max_age_hours, history_log_path):

    from dateutil.parser import isoparse
    from datetime import timedelta
    from utils.get_timestamp import get_timestamp
    from utils.load_entries_in_time_range import load_entries_in_time_range

    now = isoparse(get_timestamp())
    newest_allowed = now.isoformat()
    oldest_allowed = (now - timedelta(hours=max_age_hours)).isoformat()

    return load_entries_in_time_range(
        file_path=history_log_path,
        start_time=oldest_allowed,
        end_time=newest_allowed
    )

def datetime_manager(mode=None, config: dict = None):
    from dateutil.parser import isoparse
    from datetime import timedelta
    from utils.get_timestamp import get_timestamp

    timestamp = get_timestamp()
    now = isoparse(timestamp)
    current_day = now.strftime("%d-%m-%Y")

    yesterday_datetime = now - timedelta(days=1)
    yesterday = yesterday_datetime.strftime("%d-%m-%Y")

    # Week start configurable (default monday)
    week_start_day = (config or {}).get("datetime", {}).get("week_start_day", "monday").lower()
    weekday = now.weekday()  # Monday=0

    if week_start_day == "monday":
        last_monday = now - timedelta(days=weekday + 7)
    elif week_start_day == "sunday":
        last_monday = now - timedelta(days=(weekday + 8) % 7 + 7)
    else:
        last_monday = now - timedelta(days=weekday + 7)  # fallback monday

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

def get_archive_log_paths(datetime_data, config: dict = None):
    cfg = (config or {}).get("paths", {})
    archive_log_path = cfg.get("archive_folder", "../AI-crypto-trader-logs/analysis_logs/history_archives/")
    extension = cfg.get("extension", ".jsonl")
    base_name = cfg.get("base_log_name", "history_analyzer_log_")

    daily_log_name = f"{base_name}daily_{datetime_data['yesterday']}"
    weekly_log_name = f"{base_name}weekly_{datetime_data['week']}"
    monthly_log_name = f"{base_name}monthly_{datetime_data['last_month']}"

    return {
        "log_path": archive_log_path,
        "daily_log_name": daily_log_name,
        "weekly_log_name": weekly_log_name,
        "monthly_log_name": monthly_log_name,
        "daily_log_path": os.path.join(archive_log_path, f"{daily_log_name}{extension}"),
        "weekly_log_path": os.path.join(archive_log_path, f"{weekly_log_name}{extension}"),
        "monthly_log_path": os.path.join(archive_log_path, f"{monthly_log_name}{extension}")
    }