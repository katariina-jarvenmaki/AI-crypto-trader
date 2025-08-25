# modules/history_archiver/remove_old_archives.py
# version 2.0, aug 2025

import os
import re
from datetime import datetime, timedelta
from dateutil.parser import parse as dateparse

def remove_old_archives(logs_path: str):

    archive_log_path = os.path.join(logs_path, "history_archives")
    
    if not os.path.exists(archive_log_path):
        print(f"Path not found: {archive_log_path}")
        return
    
    # Age limit
    now = datetime.now()
    cutoff_date = now - timedelta(days=365 + 31)
    
    daily_pattern = re.compile(r"history_analyzer_log_daily_(\d{2}-\d{2}-\d{4})\.jsonl")
    weekly_pattern = re.compile(r"history_analyzer_log_weekly_(\d{2}-\d{2}-\d{4})_to_(\d{2}-\d{2}-\d{4})\.jsonl")
    monthly_pattern = re.compile(r"history_analyzer_log_monthly_(\d{2}-\d{4})\.jsonl")
    
    for filename in os.listdir(archive_log_path):
        filepath = os.path.join(archive_log_path, filename)
        if not os.path.isfile(filepath):
            continue
        
        file_date = None
        
        if daily_match := daily_pattern.match(filename):
            file_date = datetime.strptime(daily_match.group(1), "%d-%m-%Y")
        
        elif weekly_match := weekly_pattern.match(filename):
            file_date = datetime.strptime(weekly_match.group(2), "%d-%m-%Y")
        
        elif monthly_match := monthly_pattern.match(filename):
            file_date = datetime.strptime(monthly_match.group(1), "%m-%Y")
        
        if file_date and file_date < cutoff_date:
            try:
                os.remove(filepath)
                print(f"Removed old archive: {filename}")
            except Exception as e:
                print(f"Error removing {filename}: {e}")

    print("⏭  Skipping Removing old archives, because no old archives to delete")
