# modules/history_analyzer/history_archiver.py

import os
import json
from dateutil.parser import isoparse
from typing import Dict, Tuple, List
from datetime import datetime, timedelta
from modules.history_analyzer.config_history_analyzer import CONFIG

def history_archiver():

    archive_previous_day_logs()

def archive_previous_day_logs():
    logs_path = CONFIG["daily_logs_path"]
    history_log_path = CONFIG["history_log_path"]

    yesterday_dt = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday_dt.strftime("%Y-%m-%d")

    # Luo tiedostopolku ja varmista että se on olemassa
    daily_log_file = ensure_previous_day_log_file_exists(logs_path)

    # Jos tiedostossa on jo rivejä, oletetaan että arkistointi on tehty
    if os.path.exists(daily_log_file):
        with open(daily_log_file, "r") as f:
            line_count = sum(1 for _ in f)
        if line_count > 0:
            print(f"[INFO] Archive already exists with {line_count} entries for {yesterday_str}, skipping.")
            return

    # Hae eilisen merkinnät päätason historiasta
    yesterdays_entries = read_entries_for_date(history_log_path, yesterday_str)
    if not yesterdays_entries:
        print(f"[INFO] No entries found for {yesterday_str}")
        return

    # Kirjoita eilisen tiedot päiväkohtaiseen tiedostoon
    write_entries_to_file(yesterdays_entries, daily_log_file)

    # Suodata säilytettävät merkinnät ja ylikirjoita historia
    retained = retain_last_entry_per_hour_per_symbol(yesterdays_entries)
    rewrite_log_without_old_entries(history_log_path, yesterday_str, retained)

    print(f"[✔] Archived {len(yesterdays_entries)} entries to {daily_log_file}")
    print(f"[✔] Cleaned to {len(retained)} hourly last entries per symbol")

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

from typing import Dict, Tuple
from dateutil.parser import isoparse

def retain_last_entry_per_hour_per_symbol(entries: List[dict]) -> List[dict]:
    print(f"[DEBUG] Processing {len(entries)} entries for retention logic...")
    latest_entries: Dict[Tuple[str, str], dict] = {}
    skipped_missing_data = 0
    parse_errors = 0
    updated = 0
    total_considered = 0

    for entry in entries:
        ts_str = entry.get("timestamp")
        symbol = entry.get("symbol")
        if not ts_str or not symbol:
            skipped_missing_data += 1
            continue

        try:
            ts_dt = isoparse(ts_str)
            hour_key = ts_dt.strftime("%Y-%m-%dT%H")
            key = (symbol, hour_key)
            total_considered += 1

            if key not in latest_entries:
                latest_entries[key] = entry
                updated += 1
            else:
                existing_ts = isoparse(latest_entries[key]["timestamp"])
                if ts_dt > existing_ts:
                    latest_entries[key] = entry
                    updated += 1

        except Exception as e:
            parse_errors += 1
            print(f"[WARN] Failed to parse timestamp '{ts_str}': {e}")
            continue

    print(f"[INFO] Entries considered: {total_considered}")
    print(f"[INFO] Updated entries retained: {updated}")
    print(f"[INFO] Skipped entries due to missing data: {skipped_missing_data}")
    print(f"[INFO] Skipped entries due to parsing errors: {parse_errors}")
    print(f"[INFO] Total retained entries: {len(latest_entries)}")

    # Sortataan aikaleiman mukaan ennen palautusta
    return sorted(latest_entries.values(), key=lambda e: isoparse(e["timestamp"]))

def rewrite_log_without_old_entries(source_file: str, date_str: str, retained_entries: List[dict]):
    print(f"[DEBUG] Rewriting log file: {source_file}")
    print(f"[DEBUG] Retaining {len(retained_entries)} entries for date: {date_str}")

    new_lines = []
    retained_keys = {(e["symbol"], e["timestamp"]) for e in retained_entries}
    total_lines = 0
    retained_count = 0
    skipped_date_count = 0
    parse_errors = 0

    with open(source_file, "r") as f:
        for line in f:
            total_lines += 1
            try:
                entry = json.loads(line.strip())
                ts = entry.get("timestamp", "")
                symbol = entry.get("symbol", "")
                if ts.startswith(date_str):
                    if (symbol, ts) in retained_keys:
                        new_lines.append(json.dumps(entry))
                        retained_count += 1
                    else:
                        continue
                else:
                    new_lines.append(json.dumps(entry))
                    skipped_date_count += 1
            except json.JSONDecodeError as e:
                parse_errors += 1
                print(f"[WARN] JSON decode error: {e}")
                continue

    print(f"[INFO] Total lines processed: {total_lines}")
    print(f"[INFO] Retained entries for {date_str}: {retained_count}")
    print(f"[INFO] Entries from other dates retained: {skipped_date_count}")
    print(f"[INFO] Lines skipped due to parsing errors: {parse_errors}")

    # Sortataan aikaleiman mukaan ennen tallennusta
    try:
        new_lines_sorted = sorted(
            new_lines,
            key=lambda line: isoparse(json.loads(line)["timestamp"])
        )
    except Exception as e:
        print(f"[ERROR] Sorting failed: {e}")
        new_lines_sorted = new_lines  # fallback ilman sorttausta

    with open(source_file, "w") as f:
        for line in new_lines_sorted:
            f.write(line + "\n")

    print(f"[✔] Rewrite completed. New total lines in file: {len(new_lines_sorted)}")

def write_entries_to_file(entries: List[dict], target_file: str):
    with open(target_file, "a") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")