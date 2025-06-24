# scripts/log_cleaner.py

import os
import json
from datetime import datetime, timedelta
import re

LOG_DIR = "logs"
SIGNALS_LATEST = os.path.join(LOG_DIR, "signals_log.json")

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def extract_date_from_log_entry(entry):
    timestamp = entry.get("log") or entry.get("rsi") or entry.get("started_on")
    if timestamp:
        return datetime.fromisoformat(timestamp.split("+")[0])
    return None

def archive_complete_logs():
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    archive_filename = f"signals_log_{yesterday.day}-{yesterday.month}-{yesterday.year}.json"
    archive_path = os.path.join(LOG_DIR, archive_filename)

    if not os.path.exists(SIGNALS_LATEST):
        print("No signals_log.json found.")
        return

    current_data = load_json(SIGNALS_LATEST)
    archive_data = {}

    for pair, timeframes in list(current_data.items()):
        for tf, actions in list(timeframes.items()):
            for direction, log_data in list(actions.items()):
                log_date = extract_date_from_log_entry(log_data)
                if (
                    log_date
                    and log_date.date() == yesterday.date()
                    and log_data.get("status") == "complete"
                ):
                    archive_data.setdefault(pair, {}).setdefault(tf, {})[direction] = log_data
                    del current_data[pair][tf][direction]

            # Clean up empty structures
            if not current_data[pair][tf]:
                del current_data[pair][tf]
        if not current_data[pair]:
            del current_data[pair]

    if archive_data:
        save_json(archive_path, archive_data)
        save_json(SIGNALS_LATEST, current_data)
        print(f"\nArchived complete signals to {archive_filename}")

def remove_old_archives(months=2):
    cutoff_date = datetime.now() - timedelta(days=30 * months)
    pattern = re.compile(r"signals_log_(\d{1,2})-(\d{1,2})-(\d{4}).json")

    for filename in os.listdir(LOG_DIR):
        match = pattern.match(filename)
        if match:
            day, month, year = map(int, match.groups())
            try:
                file_date = datetime(year, month, day)
                if file_date < cutoff_date:
                    os.remove(os.path.join(LOG_DIR, filename))
                    print(f"Removed old archive: {filename}")
            except ValueError:
                print(f"Invalid date in filename: {filename}")

def run_log_cleanup():
    archive_complete_logs()
    remove_old_archives()

if __name__ == "__main__":
    run_log_cleanup()
