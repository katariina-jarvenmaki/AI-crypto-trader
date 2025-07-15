# scripts/log_cleaner.py

import os
import json
from datetime import datetime, timedelta
import re
import tempfile
import shutil

LOG_DIR = "logs"
SIGNALS_LATEST = os.path.join(LOG_DIR, "signals_log.json")
ORDERS_LATEST = os.path.join(LOG_DIR, "order_log.json")

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data, allow_empty_overwrite=False):

    if os.path.exists(path):
        existing = load_json(path)
        if existing and not data and not allow_empty_overwrite:
            print(f"Warning: Attempt to overwrite non-empty file {path} with empty data.")
            return

    # Save to a temp file first to avoid corruption during write
    tmp_fd, tmp_path = tempfile.mkstemp()
    with os.fdopen(tmp_fd, 'w') as tmp_file:
        json.dump(data, tmp_file, indent=4)
    shutil.move(tmp_path, path)

def extract_date_from_signal_entry(entry):
    if not isinstance(entry, dict):
        return None

    for key, signal_data in entry.items():
        if isinstance(signal_data, dict) and signal_data.get("status") == "completed":
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

    if os.path.exists(archive_path):
        print(f"Archive already exists for signals: {archive_filename}, skipping.")
        return

    current_data = load_json(SIGNALS_LATEST)
    archive_data = {}

    for pair, timeframes in list(current_data.items()):
        for tf, actions in list(timeframes.items()):
            for direction, indicators in list(actions.items()):
                if not isinstance(indicators, dict):
                    continue
                for indicator, log_data in list(indicators.items()):
                    log_date = extract_date_from_signal_entry({indicator: log_data})
                    archive_this = False

                    if log_date:
                        if log_date.date() < yesterday.date():
                            archive_this = True
                        elif log_date.date() == yesterday.date() and log_data.get("status") == "completed":
                            archive_this = True

                    if archive_this:
                        print(f"Archiving signal: {pair} {tf} {direction} {indicator} @ {log_date}")
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
        save_json(ORDERS_LATEST, current_data, allow_empty_overwrite=True)
        print(f"Archived complete orders to {archive_filename}")

def archive_old_orders():
    if not os.path.exists(ORDERS_LATEST):
        print("No order_log.json found.")
        return

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    archive_filename = f"order_log_{yesterday.day}-{yesterday.month}-{yesterday.year}.json"
    archive_path = os.path.join(LOG_DIR, archive_filename)

    if os.path.exists(archive_path):
        print(f"Archive already exists for orders: {archive_filename}, skipping.")
        return

    current_data = load_json(ORDERS_LATEST)
    archive_data = {}

    for symbol, timeframes in list(current_data.items()):
        for tf, directions in list(timeframes.items()):
            for direction, indicators in list(directions.items()):
                if not isinstance(indicators, dict):
                    continue
                for indicator, log_data in list(indicators.items()):
                    timestamp = log_data.get("time") or log_data.get("started_on")
                    log_date = None
                    try:
                        if timestamp:
                            log_date = datetime.fromisoformat(timestamp.split("+")[0])
                    except Exception:
                        pass

                    archive_this = False
                    if log_date:
                        if log_date.date() < yesterday.date():
                            archive_this = True
                        elif log_date.date() == yesterday.date() and log_data.get("status") == "completed":
                            archive_this = True

                    if archive_this:
                        print(f"Archiving order: {symbol} {tf} {direction} {indicator} @ {log_date}")
                        archive_data.setdefault(symbol, {}).setdefault(tf, {}).setdefault(direction, {})[indicator] = log_data
                        del current_data[symbol][tf][direction][indicator]

                if not current_data[symbol][tf][direction]:
                    del current_data[symbol][tf][direction]
            if not current_data[symbol][tf]:
                del current_data[symbol][tf]
        if not current_data[symbol]:
            del current_data[symbol]

    if archive_data:
        save_json(archive_path, archive_data)
        save_json(ORDERS_LATEST, current_data, allow_empty_overwrite=True)
        print(f"Archived complete orders to {archive_filename}")
    else:
        print("No orders to archive.")

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

def clean_symbol_data_log(file_path="modules/symbol_data_fetcher/symbol_data_log.jsonl", days=30):
    if not os.path.exists(file_path):
        print(f"{file_path} not found.")
        return

    cutoff = datetime.now() - timedelta(days=days)
    temp_path = file_path + ".tmp"

    kept = 0
    removed = 0
    with open(file_path, "r") as infile, open(temp_path, "w") as outfile:
        for line in infile:
            try:
                data = json.loads(line)
                ts_str = data.get("timestamp") or data.get("time") or data.get("date")
                if ts_str:
                    ts = datetime.fromisoformat(ts_str.split("+")[0])
                    if ts >= cutoff:
                        outfile.write(line)
                        kept += 1
                    else:
                        removed += 1
                else:
                    outfile.write(line)
                    kept += 1
            except Exception as e:
                # Malformed line? Keep it just in case
                print(f"Error parsing line: {e}")
                outfile.write(line)
                kept += 1

    shutil.move(temp_path, file_path)
    print(f"Cleaned symbol_data_log.jsonl: kept {kept}, removed {removed} old entries.")

def delete_temporary_logs(directories, prefix="temporary_", suffix=".jsonl"):
    deleted_files = []
    for directory in directories:
        if not os.path.exists(directory):
            continue
        for fname in os.listdir(directory):
            if fname.startswith(prefix) and fname.endswith(suffix):
                fpath = os.path.join(directory, fname)
                try:
                    os.remove(fpath)
                    deleted_files.append(fpath)
                except Exception as e:
                    print(f"Failed to delete {fpath}: {e}")
    if deleted_files:
        print("Deleted temporary log files:")
        for f in deleted_files:
            print(f" - {f}")
    else:
        print("No temporary log files found to delete.")

def run_log_cleanup():
    archive_complete_signals()
    archive_old_orders()
    remove_old_archives()
    clean_symbol_data_log()
    delete_temporary_logs([
        "modules/symbol_data_fetcher",
        "logs/cron"
    ])

if __name__ == "__main__":
    run_log_cleanup()
