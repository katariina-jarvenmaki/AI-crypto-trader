import os
import json
from datetime import datetime

def archive_analysis(mode, entries, datetime_data, log_path):

    if mode not in ["daily", "weekly", "monthly"]:
        raise ValueError(f"Invalid mode: {mode}")

    flattened_entries = flatten_analysis_entries(entries)

    # Go through the entries
    for i, entry in enumerate(flattened_entries):
        
        ts = entry.get('timestamp')
        # print(ts)

#         if ts is None:
#             print(f"[WARNING] Entry {i} missing 'timestamp': {entry}")
#         else:
#             print(f"[INFO] Entry {i} timestamp: {ts}")

#     if mode == "daily":
#         target_date = datetime.fromisoformat(datetime_data["yesterday_datetime"])
#         for e in entries:
#             ts_date = parse_ts(e["timestamp"]).date()
#             print(f"[DEBUG] Entry date: {ts_date}, Target: {target_date.date()}")
#             if ts_date == target_date.date():
#                 filtered_entries.append(e)

#     elif mode == "weekly":
#         week_dates = [datetime.strptime(d, "%d-%m-%Y").date() for d in datetime_data["week_dates"]]
#         for e in entries:
#             ts_date = parse_ts(e["timestamp"]).date()
#             print(f"[DEBUG] Entry date: {ts_date}, Week Dates: {week_dates}")
#             if ts_date in week_dates:
#                 filtered_entries.append(e)

#     elif mode == "monthly":
#         start = datetime.fromisoformat(datetime_data["first_day_last_month"])
#         end = datetime.fromisoformat(datetime_data["last_day_last_month"])
#         for e in entries:
#             ts_date = parse_ts(e["timestamp"]).date()
#             print(f"[DEBUG] Entry date: {ts_date}, Range: {start.date()} - {end.date()}")
#             if start.date() <= ts_date <= end.date():
#                 filtered_entries.append(e)

#     print(f"[RESULT] Filtered {len(filtered_entries)} entries for mode {mode}")
#     for entry in filtered_entries:
#         print(entry)

# WEEKLY DATA:
#     current_day = first_day_last_month
#     monthly_entries = []
#     while current_day <= last_day_last_month:
#         date_str = current_day.strftime("%Y-%m-%d")
#         monthly_entries.extend(read_entries_by_date(analysis_log_path, date_str))
#         current_day += timedelta(days=1)

#     week_dates = [(last_monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
#     weekly_entries = []
#     for date_str in week_dates:
#         weekly_entries.extend(read_entries_by_date(analysis_log_path, date_str))

#     entries = read_entries_by_date(analysis_log_path, yesterday_str)

# DAILY DATA:

#     if not entries:
#         print(f"[INFO] No analysis entries found for {yesterday_str}")
#         return

#     write_entries_to_file(entries, daily_log_file)
#     retained = retain_last_hourly_entry_per_symbol(entries)
#     rewrite_log_with_retained_entries_only(analysis_log_path, yesterday_str, retained)

#     print(f"[✔] Archived {len(entries)} analysis entries to {daily_log_file}")
#     print(f"[✔] Cleaned to {len(retained)} hourly last entries per symbol")

# MONHTLY DATA:

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




    # if(mode == "daily"):
    # elif(mode == "weekly"):
    # elif(mode == "monthly"):


    # print(f"log_path: {log_path}")
    # print(f"entries: {entries}")

    # print(f"today: {datetime_data['current_day']}")
    # print(f"first_day_this_month: {datetime_data['first_day_this_month']}")
    # print(f"last_day_last_month: {datetime_data['clast_day_last_month']}")
    # print(f"first_day_last_month: {datetime_data['first_day_last_month']}")


    

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

def flatten_analysis_entries(entries):

    if isinstance(entries, dict):
        entries = [entries]
    elif not isinstance(entries, list):
        raise ValueError("Entries must be a list of dict or a single dict object")

    if not all(isinstance(e, dict) for e in entries):
        raise ValueError("All entries must be dict objects")

    flattened_entries = []

    for symbol, symbol_entries in entries[0].items():
        for e in symbol_entries:
            e['symbol'] = symbol
            flattened_entries.append(e)

    return flattened_entries