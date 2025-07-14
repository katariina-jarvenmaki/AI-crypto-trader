# modules/history_analyzer/history_archiver.py

import os
import json
from typing import List
from datetime import datetime, timedelta
from modules.history_analyzer.config_history_analyzer import CONFIG

def history_archiver():

    archive_previous_day_logs()

def archive_previous_day_logs():

    logs_path = CONFIG["daily_logs_path"]
    history_log_path = CONFIG["history_log_path"]

    yesterday_dt = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday_dt.strftime("%Y-%m-%d")

    daily_log_file = ensure_previous_day_log_file_exists(logs_path)
    yesterdays_entries = read_entries_for_date(history_log_path, yesterday_str)

    if not yesterdays_entries:
        print(f"No entries found for {yesterday_str}")
        return

    write_entries_to_file(yesterdays_entries, daily_log_file)

    retained = retain_last_entry_per_hour_per_symbol(yesterdays_entries)
    rewrite_log_without_old_entries(history_log_path, yesterday_str, retained)

    print(f"✔ Archived {len(yesterdays_entries)} entries to {daily_log_file}")
    print(f"✔ Cleaned to {len(retained)} hourly last entries per symbol")

def ensure_previous_day_log_file_exists(logs_path: str) -> str:
    yesterday = datetime.now() - timedelta(days=1)
    filename = f"history_data_log_day_{yesterday.strftime('%d_%m_%Y')}.jsonl"
    log_file_path = os.path.join(logs_path, filename)
    if not os.path.exists(log_file_path):
        open(log_file_path, "w").close()
    return log_file_path

def read_entries_for_date(file_path: str, date_str: str) -> List[dict]:
    results = []
    with open(file_path, "r") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                timestamp = entry.get("timestamp")
                if timestamp and timestamp.startswith(date_str):
                    results.append(entry)
            except json.JSONDecodeError:
                continue
    return results

def retain_last_entry_per_hour_per_symbol(entries: List[dict]) -> List[dict]:
    latest_entries: Dict[Tuple[str, str], dict] = {}

    for entry in entries:
        ts_str = entry.get("timestamp")
        symbol = entry.get("symbol")
        if not ts_str or not symbol:
            continue

        try:
            ts_dt = isoparse(ts_str)  # Säilytä alkuperäinen aikavyöhyke
            hour_key = ts_dt.strftime("%Y-%m-%dT%H")  # esim. "2025-07-11T17"
            key = (symbol, hour_key)

            if key not in latest_entries or ts_dt > isoparse(latest_entries[key]["timestamp"]):
                latest_entries[key] = entry

        except Exception as e:
            continue  # virheelliset timestampit ohitetaan

    return list(latest_entries.values())

def rewrite_log_without_old_entries(source_file: str, date_str: str, retained_entries: List[dict]):
    new_lines = []
    retained_keys = {(e["symbol"], e["timestamp"]) for e in retained_entries}

    with open(source_file, "r") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                ts = entry.get("timestamp", "")
                symbol = entry.get("symbol", "")
                if ts.startswith(date_str):
                    if (symbol, ts) in retained_keys:
                        new_lines.append(json.dumps(entry))
                else:
                    new_lines.append(json.dumps(entry))
            except json.JSONDecodeError:
                continue

    with open(source_file, "w") as f:
        for line in new_lines:
            f.write(line + "\n")

def write_entries_to_file(entries: List[dict], target_file: str):
    with open(target_file, "a") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")