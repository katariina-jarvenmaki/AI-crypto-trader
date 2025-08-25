# modules/history_archiver/archive_analysis.py
# version 2.0, aug 2025

import os
import json
from typing import List
from dateutil.parser import isoparse
from modules.save_and_validate.save_and_validate import save_and_validate

def archive_analysis(mode, entries, datetime_data, config, history_log_path, log_path, log_schema_path):

    if mode not in ["daily", "weekly", "monthly"]:
        raise ValueError(f"Invalid mode: {mode}")

    flattened_entries = flatten_analysis_entries(entries)

    filtered_entries = filter_analysis_entries(mode, flattened_entries, datetime_data)
    print(f"\n💹 Filtered {len(filtered_entries)} entries for mode {mode}")

    save_cfg = config.get("save", {})
    verbose = save_cfg.get("verbose", False)
    overwrite_mode = save_cfg.get("overwrite_mode", "overwrite")

    if len(filtered_entries) == 0:
        print(f"⏭  Skipping Archiving, because no analysis entries found for mode {mode}")

    else:
        # Save filtered results to archives log
        print(f"❇️  Saving new result to {log_path}")
        save_and_validate(
            data=filtered_entries,
            path=log_path,
            schema=log_schema_path,
            verbose=verbose
        )

    # Get retained entries
    retained_entries = retain_only_relevant_entries_per_symbol(mode, flattened_entries, config)
    future_entries = []
    if config.get("future_entries", {}).get(mode, True):
        future_entries = get_future_entries(mode, flattened_entries, datetime_data)

    # Combine retained and new entries
    cleaned_entries = retained_entries + future_entries
    cleaned_entries = sort_by_timestamp(cleaned_entries)

    if len(filtered_entries) == 0 or len(retained_entries) == 0:
        print(f"⏭  Skipping Rewrite, because no retained entries found for mode {mode}")

    else:
        print(f"❇️  Rewriting retained and new entries to {history_log_path}")
        save_and_validate(
            data=cleaned_entries,
            path=history_log_path,
            schema=log_schema_path,
            verbose=verbose,
            mode=overwrite_mode
        )

        print(f"[✔] Archived {len(filtered_entries)} analysis entries to {log_path}")
        print(f"[✔] Cleaned to {len(retained_entries)} last entries per symbol")

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

def retain_only_relevant_entries_per_symbol(mode, entries, config):

    from dateutil.parser import isoparse
    from typing import Dict, Tuple

    retention_cfg = config.get("retention", {
        "daily": "hourly_last",
        "weekly": "daily_last",
        "monthly": "weekly_last"
    })

    strategy = retention_cfg.get(mode, "default")

    latest: Dict[Tuple[str, str], dict] = {}

    for entry in entries:
        timestamp_str, symbol = entry.get("timestamp"), entry.get("symbol")
        if not timestamp_str or not symbol:
            continue
        try:
            ts = isoparse(timestamp_str) 
            if strategy == "hourly_last":
                key = (symbol, ts.strftime("%Y-%m-%dT%H"))
            elif strategy == "daily_last":
                key = (symbol, ts.strftime("%Y-%m-%d"))
            elif strategy == "weekly_last":
                iso_year, iso_week, _ = ts.isocalendar()
                key = (symbol, f"{iso_year}-W{iso_week:02d}")
            else:
                # fallback = timestamp day
                key = (symbol, ts.strftime("%Y-%m-%d"))

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
