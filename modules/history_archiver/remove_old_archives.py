# modules/history_archiver/remove_old_archives.py
# version 2.0, aug 2025

import os
import re
from datetime import datetime, timedelta
from dateutil.parser import parse as dateparse

def remove_old_archives(logs_path: str, config: dict):

    remove_cfg = config.get("remove_old_settings", {})
    if not remove_cfg.get("enabled", True):
        print("⏭  Skipping Removing old archives (disabled in config)")
        return

    archive_folder = remove_cfg.get("archive_folder", "history_archives")
    retention_days = remove_cfg.get("retention_days", 365 + 31)

    archive_log_path = os.path.join(logs_path, archive_folder)
    
    if not os.path.exists(archive_log_path):
        print(f"Path not found: {archive_log_path}")
        return
    
    now = datetime.now()
    cutoff_date = now - timedelta(days=retention_days)

    patterns = remove_cfg.get("patterns", {})
    date_formats = remove_cfg.get("date_formats", {})

    compiled_patterns = {
        key: re.compile(pattern) for key, pattern in patterns.items()
    }

    removed_files = 0

    for filename in os.listdir(archive_log_path):
        filepath = os.path.join(archive_log_path, filename)
        if not os.path.isfile(filepath):
            continue

        file_date = None

        # Daily
        if "daily" in compiled_patterns and (m := compiled_patterns["daily"].match(filename)):
            fmt = date_formats.get("daily", "%d-%m-%Y")
            file_date = datetime.strptime(m.group(1), fmt)

        # Weekly
        elif "weekly" in compiled_patterns and (m := compiled_patterns["weekly"].match(filename)):
            fmt = date_formats.get("weekly", "%d-%m-%Y")
            file_date = datetime.strptime(m.group(2), fmt)

        # Monthly
        elif "monthly" in compiled_patterns and (m := compiled_patterns["monthly"].match(filename)):
            fmt = date_formats.get("monthly", "%m-%Y")
            file_date = datetime.strptime(m.group(1), fmt)

        if file_date and file_date < cutoff_date:
            try:
                os.remove(filepath)
                removed_files += 1
                print(f"Removed old archive: {filename}")
            except Exception as e:
                print(f"Error removing {filename}: {e}")

    if removed_files == 0:
        print("⏭  Skipping Removing old archives, because no old archives to delete")