# scripts/log_cleaner.py

import os
import json
from datetime import datetime, timedelta
import re

LOG_DIR = "logs"
SIGNALS_LATEST = os.path.join(LOG_DIR, "signals_log.json")
ORDERS_LATEST = os.path.join(LOG_DIR, "order_log.json")

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def extract_date_from_signal_entry(entry):
    if not isinstance(entry, dict):
        return None

    for key, signal_data in entry.items():
        if isinstance(signal_data, dict) and signal_data.get("status") == "complete":
            timestamp = signal_data.get("time") or signal_data.get("started_on")
            if timestamp and isinstance(timestamp, str):
                return datetime.fromisoformat(timestamp.split("+")[0])
    return None

def extract_date_from_order_entry(entry):
    if not isinstance(entry, dict):
        return None

    timestamp = entry.get("timestamp")
    if timestamp and isinstance(timestamp, str):
        try:
            return datetime.fromisoformat(timestamp.split("+")[0])
        except ValueError:
            pass
    return None

def archive_complete_signals():
    if not os.path.exists(SIGNALS_LATEST):
        print("No signals_log.json found.")
        return

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    archive_filename = f"signals_log_{yesterday.day}-{yesterday.month}-{yesterday.year}.json"
    archive_path = os.path.join(LOG_DIR, archive_filename)

    current_data = load_json(SIGNALS_LATEST)
    archive_data = {}

    for pair, timeframes in list(current_data.items()):
        for tf, actions in list(timeframes.items()):
            for direction, indicators in list(actions.items()):
                if not isinstance(indicators, dict):
                    continue
                for indicator, log_data in list(indicators.items()):
                    log_date = extract_date_from_signal_entry({indicator: log_data})
                    if (
                        log_date
                        and log_date.date() == yesterday.date()
                        and log_data.get("status") == "complete"
                    ):
                        archive_data.setdefault(pair, {}).setdefault(tf, {}).setdefault(direction, {})[indicator] = log_data
                        del current_data[pair][tf][direction][indicator]

                if not current_data[pair][tf][direction]:
                    del current_data[pair][tf][direction]
            if not current_data[pair][tf]:
                del current_data[pair][tf]
        if not current_data[pair]:
            del current_data[pair]

    if archive_data:
        save_json(archive_path, archive_data)
        save_json(SIGNALS_LATEST, current_data)
        print(f"Archived complete signals to {archive_filename}")

def archive_old_orders():
    if not os.path.exists(ORDERS_LATEST):
        print("No order_log.json found.")
        return

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    archive_filename = f"order_log_{yesterday.day}-{yesterday.month}-{yesterday.year}.json"
    archive_path = os.path.join(LOG_DIR, archive_filename)

    current_data = load_json(ORDERS_LATEST)
    archive_data = {}

    for symbol, directions in list(current_data.items()):
        for direction in ["long", "short"]:
            orders = directions.get(direction, [])
            kept_orders = []
            archived_orders = []

            for order in orders:
                log_date = extract_date_from_order_entry(order)
                if (
                    log_date
                    and log_date.date() <= yesterday.date()
                    and order.get("status") == "complete"
                ):
                    archived_orders.append(order)
                else:
                    kept_orders.append(order)

            if archived_orders:
                archive_data.setdefault(symbol, {}).setdefault(direction, []).extend(archived_orders)
                current_data[symbol][direction] = kept_orders

        # Clean up empty directions
        if not current_data.get(symbol, {}).get("long") and not current_data.get(symbol, {}).get("short"):
            current_data.pop(symbol, None)

    if archive_data:
        save_json(archive_path, archive_data)
        save_json(ORDERS_LATEST, current_data)
        print(f"Archived complete orders to {archive_filename}")

def remove_old_archives(months=2):
    cutoff_date = datetime.now() - timedelta(days=30 * months)
    pattern = re.compile(r"(signals_log|order_log)_(\d{1,2})-(\d{1,2})-(\d{4}).json")

    for filename in os.listdir(LOG_DIR):
        match = pattern.match(filename)
        if match:
            _, day, month, year = match.groups()
            try:
                file_date = datetime(int(year), int(month), int(day))
                if file_date < cutoff_date:
                    os.remove(os.path.join(LOG_DIR, filename))
                    print(f"Removed old archive: {filename}")
            except ValueError:
                print(f"Invalid date in filename: {filename}")

def run_log_cleanup():
    archive_complete_signals()
    archive_old_orders()
    remove_old_archives()

if __name__ == "__main__":
    run_log_cleanup()
