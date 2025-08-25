# modules/history_archiver/history_archiver.py
# version 2.0, aug 2025

from utils.load_configs_and_logs import load_configs_and_logs
from modules.history_archiver.archive_analysis import archive_analysis
from modules.history_archiver.utils import analysis_entries_loader, datetime_manager, get_archive_log_paths, check_if_analysis_log_file_exists


def history_archiver(max_age_hours, history_log_path, log_schema):
    """
    Does history archiving and deleting old history archives
    """

    # Load current log entries
    analysis_entries = analysis_entries_loader(max_age_hours, history_log_path)

    # Define archive paths & filenames
    datetime_data = datetime_manager()
    archive_log_paths = get_archive_log_paths(datetime_data)

    # Check archive exisistence
    is_daily_archived = check_if_analysis_log_file_exists(archive_log_paths["daily_log_path"])
    is_weekly_archived = check_if_analysis_log_file_exists(archive_log_paths["weekly_log_path"])
    is_monthly_archived = check_if_analysis_log_file_exists(archive_log_paths["monthly_log_path"])

    # Run the archivers, if there is no existing archive 
    archive_conditions = {
        "daily": (is_daily_archived, archive_log_paths["daily_log_path"]),
        "weekly": (is_weekly_archived, archive_log_paths["weekly_log_path"]),
        "monthly": (is_monthly_archived, archive_log_paths["monthly_log_path"]),
    }

    for period, (is_archived, log_path) in archive_conditions.items():
        if not is_archived:
            archive_analysis(period, analysis_entries, datetime_data, history_log_path, log_path, log_schema)

    # REMOVING THE OLD ARCHIVERS

    # print(analysis_entries)
    # print(datetime_data)
    # print(archive_log_paths)

    # logs_path = CONFIG["analysis_daily_logs_path"]
    # weekly_log_file = os.path.join(logs_path, f"analysis_log_week_{week_str}.jsonl")
    # monthly_log_file = os.path.join(logs_path, f"analysis_log_month_{month_str}.jsonl")

    # Tarkista onko:
    # * Eiliselle jo archive
    # * Viime viikolle jo archive
    # * Viime kuulle jo archive

    # Archivin analysis logs
    # archive_analysis_logs("daily")
    # archive_analysis_logs("weekly")
    # archive_analysis_logs("monthly")

# modules/history_analyzer/history_archiver.py

# import os
# import json
# from dateutil.parser import isoparse
# from typing import Dict, Tuple, List
# from datetime import datetime, timedelta
# from modules.history_analyzer.config_history_analyzer import CONFIG
# from dateutil.tz import UTC

# def history_archiver():
#     archive_analysis_log_daily()
#     archive_analysis_log_weekly()
#     archive_analysis_log_monthly()
#     remove_old_analysis_log_entries()
#     remove_old_history_log_entries()
#     remove_old_sentiment_log_entries()

# DAILY ARCHIVE ANALYSIS LOGGING
# def archive_analysis_log_daily():
#     logs_path = CONFIG["analysis_daily_logs_path"]
#     analysis_log_path = CONFIG["analysis_log_path"]

#     yesterday_dt = datetime.now() - timedelta(days=1)
#     yesterday_str = yesterday_dt.strftime("%Y-%m-%d")

#     daily_log_file = ensure_analysis_log_file_exists(logs_path)

#     if os.path.exists(daily_log_file):
#         with open(daily_log_file, "r") as f:
#             if sum(1 for _ in f) > 0:
#                 print(f"[INFO] Analysis archive already exists for {yesterday_str}, skipping.")
#                 return

#     entries = read_entries_by_date(analysis_log_path, yesterday_str)
#     if not entries:
#         print(f"[INFO] No analysis entries found for {yesterday_str}")
#         return

#     write_entries_to_file(entries, daily_log_file)
#     retained = retain_last_hourly_entry_per_symbol(entries)
#     rewrite_log_with_retained_entries_only(analysis_log_path, yesterday_str, retained)

#     print(f"[✔] Archived {len(entries)} analysis entries to {daily_log_file}")
#     print(f"[✔] Cleaned to {len(retained)} hourly last entries per symbol")

# def retain_last_hourly_entry_per_symbol(entries: List[dict]) -> List[dict]:
#     latest: Dict[Tuple[str, str], dict] = {}
#     for entry in entries:
#         ts_str = entry.get("timestamp")
#         symbol = entry.get("symbol")
#         if not ts_str or not symbol:
#             continue
#         try:
#             ts = isoparse(ts_str)
#             hour_key = ts.strftime("%Y-%m-%dT%H")
#             key = (symbol, hour_key)
#             if key not in latest or isoparse(latest[key]["timestamp"]) < ts:
#                 latest[key] = entry
#         except Exception:
#             continue
#     return sorted(latest.values(), key=lambda e: isoparse(e["timestamp"]))

# WEEKLY ARCHIVE ANALYSIS LOGGING
# def archive_analysis_log_weekly():
#     logs_path = CONFIG["analysis_weekly_logs_path"]
#     analysis_log_path = CONFIG["analysis_log_path"]

#     today = datetime.now()
#     last_monday = today - timedelta(days=today.weekday() + 7)
#     last_sunday = last_monday + timedelta(days=6)

#     week_str = f"{last_monday.strftime('%d_%m_%Y')}_to_{last_sunday.strftime('%d_%m_%Y')}"
#     weekly_log_file = os.path.join(logs_path, f"analysis_log_week_{week_str}.jsonl")

#     if os.path.exists(weekly_log_file):
#         with open(weekly_log_file, "r") as f:
#             if sum(1 for _ in f) > 0:
#                 print(f"[INFO] Weekly analysis archive already exists for week {week_str}, skipping.")
#                 return

    # Lue kaikki merkinnät viime viikolta
#     week_dates = [(last_monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
#     weekly_entries = []
#     for date_str in week_dates:
#         weekly_entries.extend(read_entries_by_date(analysis_log_path, date_str))

#     if not weekly_entries:
#         print(f"[INFO] No analysis entries found for week {week_str}")
#         return

#     write_entries_to_file(weekly_entries, weekly_log_file)

    # Säilytä jokaiselta päivältä viimeinen kirjain jokaiselle symbolille
#     retained_weekly = retain_last_daily_entry_per_symbol(weekly_entries)

    # Pidä myös kaikki tämän viikon uudet merkinnät
#     this_week_start = last_sunday + timedelta(days=1)
#     future_entries = []
#     with open(analysis_log_path, "r") as f:
#         for line in f:
#             try:
#                 entry = json.loads(line.strip())
#                 ts = entry.get("timestamp", "")
#                 if ts:
#                     ts_dt = isoparse(ts)
#                     if ts_dt >= this_week_start:
#                         future_entries.append(entry)
#             except Exception:
#                 continue

    # Kirjoita uudelleen vain edellisten viikkojen viimeiset merkinnät ja uuden viikon kaikki merkinnät
#     cleaned_entries = retained_weekly + future_entries
#     cleaned_entries = sorted(cleaned_entries, key=lambda e: isoparse(e["timestamp"]))

#     with open(analysis_log_path, "w") as f:
#         for entry in cleaned_entries:
#             f.write(json.dumps(entry) + "\n")

#     print(f"[✔] Archived {len(weekly_entries)} entries to {weekly_log_file}")
#     print(f"[✔] Cleaned to {len(cleaned_entries)} entries (retained daily last + current week)")

# def retain_last_daily_entry_per_symbol(entries: List[dict]) -> List[dict]:
#     latest: Dict[Tuple[str, str], dict] = {}
#     for entry in entries:
#         ts_str = entry.get("timestamp")
#         symbol = entry.get("symbol")
#         if not ts_str or not symbol:
#             continue
#         try:
#             ts = isoparse(ts_str)
#             date_key = ts.strftime("%Y-%m-%d")
#             key = (symbol, date_key)
#             if key not in latest or isoparse(latest[key]["timestamp"]) < ts:
#                 latest[key] = entry
#         except Exception:
#             continue
#     return sorted(latest.values(), key=lambda e: isoparse(e["timestamp"]))

# MONTLY ARCHIVE ANALYSIS LOGGING
# def archive_analysis_log_monthly():
#     logs_path = CONFIG["analysis_monthly_logs_path"]
#     analysis_log_path = CONFIG["analysis_log_path"]

#     today = datetime.now()
#     first_day_this_month = today.replace(day=1)
#     last_day_last_month = first_day_this_month - timedelta(days=1)
#     first_day_last_month = last_day_last_month.replace(day=1)

#     month_str = first_day_last_month.strftime("%m_%Y")
#     monthly_log_file = os.path.join(logs_path, f"analysis_log_month_{month_str}.jsonl")

#     if os.path.exists(monthly_log_file):
#         with open(monthly_log_file, "r") as f:
#             if sum(1 for _ in f) > 0:
#                 print(f"[INFO] Monthly analysis archive already exists for {month_str}, skipping.")
#                 return

    # Lue kaikki merkinnät viime kuulta
#     current_day = first_day_last_month
#     monthly_entries = []
#     while current_day <= last_day_last_month:
#         date_str = current_day.strftime("%Y-%m-%d")
#         monthly_entries.extend(read_entries_by_date(analysis_log_path, date_str))
#         current_day += timedelta(days=1)

#     if not monthly_entries:
#         print(f"[INFO] No analysis entries found for month {month_str}")
#         return

#     write_entries_to_file(monthly_entries, monthly_log_file)

    # Säilytä viimeinen merkintä viikolta per symboli
#     retained_monthly = retain_last_weekly_entry_per_symbol(monthly_entries)

    # Säilytä myös kaikki uuden kuukauden merkinnät
#     future_entries = []
#     with open(analysis_log_path, "r") as f:
#         for line in f:
#             try:
#                 entry = json.loads(line.strip())
#                 ts = entry.get("timestamp", "")
#                 if ts:
#                     ts_dt = isoparse(ts)
#                     if ts_dt >= first_day_this_month:
#                         future_entries.append(entry)
#             except Exception:
#                 continue

    # Yhdistä säilytettävät ja uuden kuukauden merkinnät
#     cleaned_entries = retained_monthly + future_entries
#     cleaned_entries = sorted(cleaned_entries, key=lambda e: isoparse(e["timestamp"]))

#     with open(analysis_log_path, "w") as f:
#         for entry in cleaned_entries:
#             f.write(json.dumps(entry) + "\n")

#     print(f"[✔] Archived {len(monthly_entries)} entries to {monthly_log_file}")
#     print(f"[✔] Cleaned to {len(cleaned_entries)} entries (retained weekly last + current month)")

# def retain_last_weekly_entry_per_symbol(entries: List[dict]) -> List[dict]:
#     latest: Dict[Tuple[str, str], dict] = {}
#     for entry in entries:
#         ts_str = entry.get("timestamp")
#         symbol = entry.get("symbol")
#         if not ts_str or not symbol:
#             continue
#         try:
#             ts = isoparse(ts_str)
#             iso_year, iso_week, _ = ts.isocalendar()
#             week_key = f"{iso_year}-W{iso_week:02d}"
#             key = (symbol, week_key)
#             if key not in latest or isoparse(latest[key]["timestamp"]) < ts:
#                 latest[key] = entry
#         except Exception:
#             continue
#     return sorted(latest.values(), key=lambda e: isoparse(e["timestamp"]))

# ARCHIVE ANALYSIS LOGGIN GENERAL
# def ensure_analysis_log_file_exists(logs_path: str) -> str:
#     yesterday = datetime.now() - timedelta(days=1)
#     filename = f"analysis_log_day_{yesterday.strftime('%d_%m_%Y')}.jsonl"
#     full_path = os.path.join(logs_path, filename)
#     if not os.path.exists(full_path):
#         open(full_path, "w").close()
#     return full_path

# def read_entries_by_date(file_path: str, date_str: str) -> List[dict]:
#     results = []
#     with open(file_path, "r") as f:
#         for line in f:
#             try:
#                 entry = json.loads(line.strip())
#                 ts = entry.get("timestamp")
#                 if ts and ts.startswith(date_str):
#                     results.append(entry)
#             except json.JSONDecodeError:
#                 continue
#     return results

# def rewrite_log_with_retained_entries_only(source_file: str, date_str: str, retained: List[dict]):
#     new_lines = []
#     retained_keys = {(e["symbol"], e["timestamp"]) for e in retained}
#     with open(source_file, "r") as f:
#         for line in f:
#             try:
#                 entry = json.loads(line.strip())
#                 ts = entry.get("timestamp", "")
#                 symbol = entry.get("symbol", "")
#                 if ts.startswith(date_str):
#                     if (symbol, ts) in retained_keys:
#                         new_lines.append(json.dumps(entry))
#                 else:
#                     new_lines.append(json.dumps(entry))
#             except json.JSONDecodeError:
#                 continue

#     try:
#         new_lines = sorted(new_lines, key=lambda line: isoparse(json.loads(line)["timestamp"]))
#     except Exception:
#         pass

#     with open(source_file, "w") as f:
#         for line in new_lines:
#             f.write(line + "\n")

# def write_entries_to_file(entries: List[dict], target_file: str):
#     with open(target_file, "a") as f:
#         for entry in entries:
#             f.write(json.dumps(entry) + "\n")

# REMOVE OLD LOG ENTRIES
# def remove_old_analysis_log_entries():
#     analysis_log_path = CONFIG["analysis_log_path"]
    
    # Tee cutoff_date UTC-aikavyöhykkeellä varustettuna (jotta vertailu toimii varmasti)
#     cutoff_date = (datetime.now() - timedelta(days=60)).astimezone(UTC)

#     retained_entries = []
#     removed_count = 0
#     total_count = 0
#     skipped_invalid = 0

#     with open(analysis_log_path, "r") as f:
#         for line in f:
#             total_count += 1
#             try:
#                 entry = json.loads(line.strip())
#                 ts_str = entry.get("timestamp")
#                 if not ts_str:
#                     skipped_invalid += 1
#                     retained_entries.append(entry)  # pidetään varmuuden vuoksi
#                     continue

#                 ts = isoparse(ts_str)

                # Muunnetaan timestamp UTC:ksi ennen vertailua
#                 if ts.tzinfo is not None:
#                     ts = ts.astimezone(UTC)
#                 else:
#                     ts = ts.replace(tzinfo=UTC)

#                 if ts >= cutoff_date:
#                     retained_entries.append(entry)
#                 else:
#                     removed_count += 1

#             except Exception as e:
#                 skipped_invalid += 1
#                 retained_entries.append(entry)  # pidetään varmuuden vuoksi

    # Lajitellaan vielä varmuuden vuoksi
#     retained_entries = sorted(retained_entries, key=lambda e: isoparse(e["timestamp"]))

    # Kirjoitetaan takaisin tiedostoon
#     with open(analysis_log_path, "w") as f:
#         for entry in retained_entries:
#             f.write(json.dumps(entry) + "\n")

#     print(f"[INFO] Total entries processed: {total_count}")
#     print(f"[INFO] Entries removed (older than {cutoff_date.date()} UTC): {removed_count}")
#     print(f"[INFO] Entries with invalid or missing timestamp (retained): {skipped_invalid}")
#     print(f"[✔] Retained {len(retained_entries)} entries.")

# def remove_old_history_log_entries():
#     history_log_path = CONFIG["history_log_path"]
#     cutoff_date = (datetime.now() - timedelta(days=30)).astimezone(UTC)

#     retained_entries = []
#     removed_count = 0
#     total_count = 0
#     skipped_invalid = 0

#     with open(history_log_path, "r") as f:
#         for line in f:
#             total_count += 1
#             try:
#                 entry = json.loads(line.strip())
#                 ts_str = entry.get("timestamp")
#                 if not ts_str:
#                     skipped_invalid += 1
#                     retained_entries.append(entry)  # pidetään varmuuden vuoksi
#                     continue

#                 ts = isoparse(ts_str)
#                 if ts.tzinfo is not None:
#                     ts = ts.astimezone(UTC)
#                 else:
#                     ts = ts.replace(tzinfo=UTC)

#                 if ts >= cutoff_date:
#                     retained_entries.append(entry)
#                 else:
#                     removed_count += 1

#             except Exception:
#                 skipped_invalid += 1
#                 retained_entries.append(entry)

#     retained_entries = sorted(retained_entries, key=lambda e: isoparse(e["timestamp"]))

#     with open(history_log_path, "w") as f:
#         for entry in retained_entries:
#             f.write(json.dumps(entry) + "\n")

#     print(f"[INFO] Total history log entries processed: {total_count}")
#     print(f"[INFO] History entries removed (older than {cutoff_date.date()} UTC): {removed_count}")
#     print(f"[INFO] Invalid or missing timestamp entries (retained): {skipped_invalid}")
#     print(f"[✔] Retained {len(retained_entries)} entries in history log.")

# def remove_old_sentiment_log_entries():
#     sentiment_log_path = CONFIG["sentiment_log_path"]
#     cutoff_date = (datetime.now() - timedelta(days=30)).astimezone(UTC)

#     retained_entries = []
#     removed_count = 0
#     total_count = 0
#     skipped_invalid = 0

#     with open(sentiment_log_path, "r") as f:
#         for line in f:
#             total_count += 1
#             try:
#                 entry = json.loads(line.strip())
#                 ts_str = entry.get("timestamp")
#                 if not ts_str:
#                     skipped_invalid += 1
#                     retained_entries.append(entry)
#                     continue

#                 ts = isoparse(ts_str)
#                 if ts.tzinfo is not None:
#                     ts = ts.astimezone(UTC)
#                 else:
#                     ts = ts.replace(tzinfo=UTC)

#                 if ts >= cutoff_date:
#                     retained_entries.append(entry)
#                 else:
#                     removed_count += 1

#             except Exception:
#                 skipped_invalid += 1
#                 retained_entries.append(entry)

#     retained_entries = sorted(retained_entries, key=lambda e: isoparse(e["timestamp"]))

#     with open(sentiment_log_path, "w") as f:
#         for entry in retained_entries:
#             f.write(json.dumps(entry) + "\n")

#     print(f"[INFO] Total sentiment entries processed: {total_count}")
#     print(f"[INFO] Sentiment entries removed (older than {cutoff_date.date()} UTC): {removed_count}")
#     print(f"[INFO] Invalid or missing timestamp entries (retained): {skipped_invalid}")
#     print(f"[✔] Retained {len(retained_entries)} sentiment log entries.")

if __name__ == "__main__":

    print(f"\nRunning History Archiver...\n")

    configs_and_logs = load_configs_and_logs([
        {
            "name": "history",
            "mid_folder": "analysis",
            "module_key": "history_analyzer",
            "extension": ".jsonl",
            "return": ["config", "full_log_path", "full_log_schema_path", "logs_path", "log"]
        }
    ])

    history_config = configs_and_logs["history_config"]
    history_log_path = configs_and_logs.get("history_full_log_path")
    history_log_schema_path = configs_and_logs.get("history_full_log_schema_path")
    logs_path = configs_and_logs.get("history_logs_path")
    log = configs_and_logs.get("history_log")
    
    print(f"history_config: {history_config}")
    print(f"history_log_path: {history_log_path}")
    print(f"history_log_schema_path: {history_log_schema_path}")
    print(f"logs_path: {logs_path}")
    print(f"log: {log}")

    history_archiver(max_age_hours=1500, history_log_path=history_log_path, log_schema=history_log_schema_path)