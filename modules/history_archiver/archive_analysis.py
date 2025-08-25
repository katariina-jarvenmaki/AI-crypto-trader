import os
import json
from typing import List
from dateutil.parser import isoparse
from modules.save_and_validate.save_and_validate import save_and_validate

def archive_analysis(mode, entries, datetime_data, history_log_path, log_path, log_schema_path):

    if mode not in ["daily", "weekly", "monthly"]:
        raise ValueError(f"Invalid mode: {mode}")

    flattened_entries = flatten_analysis_entries(entries)

    filtered_entries = filter_analysis_entries(mode, flattened_entries, datetime_data)
    print(f"\n💹 Filtered {len(filtered_entries)} entries for mode {mode}")

    if len(filtered_entries) == 0:
        print(f"⏭  Skipping Archieving, because no analysis entries found for mode {mode}")

    else:
        # Save filtered results to archives log
        print(f"❇️  Saving new result to {log_path}")
        save_and_validate(
            data=filtered_entries,
            path=log_path,
            schema=log_schema_path,
            verbose=False
        )

    # Get retained entries
    retained_entries = retain_only_relevant_entries_per_symbol(mode, flattened_entries)
    future_entries = get_future_entries(mode, flattened_entries, datetime_data)

    # Combine retained and new entries
    cleaned_entries = retained_entries + future_entries
    cleaned_entries = sort_by_timestamp(cleaned_entries)

    if len(filtered_entries) == 0 or len(retained_entries) == 0:
        print(f"⏭  Skipping Rewrite, because no retained entries found for mode {mode}")

    else:
        # Retained + new results to archives log
        print(f"❇️  Rewriting retained and new entries to {history_log_path}")
        save_and_validate(
            data=cleaned_entries,
            path=history_log_path,
            schema=log_schema_path,
            verbose=False,
            mode="overwrite"
        )

        print(f"[✔] Archived {len(filtered_entries)} analysis entries to {log_path}")
        print(f"[✔] Cleaned to {len(retained_entries)} hourly last entries per symbol")

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

def filter_analysis_entries(mode, flattened_entries, datetime_data):

    from datetime import datetime

    filtered_entries = []

    for entry in flattened_entries:
        ts_date = datetime.fromisoformat(entry.get('timestamp')).date()

        if mode == "daily":
            target_date = datetime.fromisoformat(datetime_data["yesterday_datetime"]).date()
            # print(f"[DEBUG] Entry date: {ts_date}, Target: {target_date}")
            if ts_date == target_date:
                filtered_entries.append(entry)

        elif mode == "weekly":
            week_dates = [datetime.strptime(d, "%d-%m-%Y").date() for d in datetime_data["week_dates"]]
            # print(f"[DEBUG] Entry date: {ts_date}, Week Dates: {week_dates}")
            if ts_date in week_dates:
                filtered_entries.append(entry)

        elif mode == "monthly":
            start = datetime.fromisoformat(datetime_data["first_day_last_month"]).date()
            end = datetime.fromisoformat(datetime_data["last_day_last_month"]).date()
            # print(f"[DEBUG] Entry date: {ts_date}, Range: {start} - {end}")
            if start <= ts_date <= end:
                filtered_entries.append(entry)

    return filtered_entries

def sort_by_timestamp(entries: List[dict]) -> List[dict]:
    return sorted(entries, key=lambda e: isoparse(e["timestamp"]))

def retain_only_relevant_entries_per_symbol(mode, entries):

    from dateutil.parser import isoparse
    from typing import Dict, Tuple

    latest: Dict[Tuple[str, str], dict] = {}

    for entry in entries:
        timestamp_str, symbol = entry.get("timestamp"), entry.get("symbol")
        if not timestamp_str or not symbol:
            continue
        try:
            ts = isoparse(timestamp_str) 
            if(mode == "daily"):
                key = (symbol, ts.strftime("%Y-%m-%dT%H")) 
                # print(f"KEY: {key}")
                if key not in latest or isoparse(latest[key]["timestamp"]) < ts:
                    latest[key] = entry
            elif(mode == "weekly"):  
                key = (symbol, ts.strftime("%Y-%m-%d"))
                # print(f"KEY: {key}")
                if key not in latest or isoparse(latest[key]["timestamp"]) < ts:
                    latest[key] = entry
            elif(mode == "monthly"):  
                iso_year, iso_week, _ = ts.isocalendar()
                key = (symbol, f"{iso_year}-W{iso_week:02d}")
                if key not in latest or isoparse(latest[key]["timestamp"]) < ts:
                    latest[key] = entry
        except Exception as e:
            print(f"Virhe: {e}")
            continue

    return sort_by_timestamp(list(latest.values()))

def get_future_entries(mode, flattened_entries, datetime_data):
    from datetime import datetime

    future_entries = []
    for entry in flattened_entries:
        ts_date = datetime.fromisoformat(entry.get('timestamp')).date()

        if mode == "daily":
            today = datetime.now().date()
            if ts_date >= today:
                future_entries.append(entry)

        elif mode == "weekly":
            first_day_this_week = datetime_data.get("first_day_this_week")
            if first_day_this_week:
                first_day_this_week = datetime.fromisoformat(first_day_this_week).date()
                if ts_date >= first_day_this_week:
                    future_entries.append(entry)

        elif mode == "monthly":
            first_day_this_month = datetime_data.get("first_day_this_month")
            if first_day_this_month:
                first_day_this_month = datetime.fromisoformat(first_day_this_month).date()
                if ts_date >= first_day_this_month:
                    future_entries.append(entry)

    return future_entries
