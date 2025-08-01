import os
import json
from datetime import datetime, timedelta
import re
import tempfile
import shutil

SIGNAL_DIR = "../AI-crypto-trader-logs/signal-data"
ORDER_DIR = "../AI-crypto-trader-logs/order-data"
SKIPPED_ORDERS_PATH = os.path.join(ORDER_DIR, "skipped_orders.json")

SIGNALS_LATEST = os.path.join(SIGNAL_DIR, "signals_log.json")
ORDERS_LATEST = os.path.join(ORDER_DIR, "order_log.json")

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        try:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse {path}: {e}")
            return {}

def save_json(path, data, allow_empty_overwrite=False):
    if os.path.exists(path):
        existing = load_json(path)
        if existing and not data and not allow_empty_overwrite:
            print(f"Warning: Attempt to overwrite non-empty file {path} with empty data.")
            return

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
    archive_path = os.path.join(SIGNAL_DIR, archive_filename)

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
        save_json(SIGNALS_LATEST, current_data, allow_empty_overwrite=True)
        print(f"Archived complete signals to {archive_filename}")

def archive_old_orders():
    if not os.path.exists(ORDERS_LATEST):
        print("No order_log.json found.")
        return

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    archive_filename = f"order_log_{yesterday.day}-{yesterday.month}-{yesterday.year}.json"
    archive_path = os.path.join(ORDER_DIR, archive_filename)

    if os.path.exists(archive_path):
        print(f"Archive already exists for orders: {archive_filename}, skipping.")
        return

    current_data = load_json(ORDERS_LATEST)
    archive_data = {}

    for symbol, timeframes in list(current_data.items()):
        for tf, directions in list(timeframes.items()):
            if not isinstance(directions, dict):
                print(f"Warning: Expected dict, got {type(directions)} in {symbol}/{tf}, skipping.")
                continue

            for direction, indicators in list(directions.items()):
                if not isinstance(indicators, dict):
                    print(f"Warning: Expected dict, got {type(indicators)} in {symbol}/{tf}/{direction}, skipping.")
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

    for base_dir in [SIGNAL_DIR, ORDER_DIR]:
        for filename in os.listdir(base_dir):
            match = pattern.match(filename)
            if match:
                _, day, month, year = match.groups()
                try:
                    file_date = datetime(int(year), int(month), int(day))
                    if file_date < cutoff_date:
                        os.remove(os.path.join(base_dir, filename))
                        print(f"Removed old archive: {filename}")
                except ValueError:
                    print(f"Invalid date in filename: {filename}")

def clean_skipped_orders_log(path=SKIPPED_ORDERS_PATH, max_age_hours=24):
    if not os.path.exists(path):
        print(f"{os.path.basename(path)} not found.")
        return

    now = datetime.now()
    cutoff = now - timedelta(hours=max_age_hours)

    entries = None

    try:
        with open(path, "r") as f:
            entries = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error loading {os.path.basename(path)}: {e}")
        try:
            # Näytä tiedoston loppu debuggausta varten
            with open(path, "r") as f:
                lines = f.readlines()
                print("Last few lines for inspection:")
                print("".join(lines[-5:]))
        except Exception as e2:
            print(f"Failed to read lines from {os.path.basename(path)}: {e2}")

        # 🔧 Yritä automaattista korjausta
        print(f"Attempting to recover {os.path.basename(path)}...")

        recovered = []
        try:
            with open(path, "r") as f:
                raw = f.read()

                # Poista alun ja lopun hakasulkeet jos on JSON-lista
                if raw.startswith("[") and raw.endswith("]"):
                    raw = raw[1:-1]

                # Erota rivit jotka näyttävät olevan objekteja
                lines = raw.splitlines()
                for line in lines:
                    line = line.strip().rstrip(",")
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                        if isinstance(item, dict):
                            recovered.append(item)
                    except Exception:
                        continue

            if recovered:
                print(f"✅ Recovered {len(recovered)} entries from damaged {os.path.basename(path)}")

                # Korvaa alkuperäinen tiedosto korjatulla versiolla
                with open(path, "w") as f:
                    json.dump(recovered, f, indent=4)

                entries = recovered  # Käytä korjattua listaa jatkossa
            else:
                print(f"❌ No valid entries recovered from {os.path.basename(path)}.")
                return

        except Exception as e3:
            print(f"Recovery failed: {e3}")
            return

    except Exception as e:
        print(f"Error loading {os.path.basename(path)}: {e}")
        return

    if not isinstance(entries, list):
        print(f"Unexpected format in {os.path.basename(path)}, expected list.")
        return

    # ✂️ Suorita varsinainen siivous
    kept_entries = []
    removed_count = 0
    for entry in entries:
        if not isinstance(entry, dict):
            print(f"⚠️ Skipping non-dict entry: {type(entry)}")
            continue

        ts_str = entry.get("timestamp")
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str.split("+")[0])
                if ts >= cutoff:
                    kept_entries.append(entry)
                else:
                    removed_count += 1
            except ValueError:
                print(f"Invalid timestamp in entry: {ts_str}, keeping it.")
                kept_entries.append(entry)
        else:
            kept_entries.append(entry)

    with open(path, "w") as f:
        json.dump(kept_entries, f, indent=4)

    print(f"Cleaned {os.path.basename(path)}: removed {removed_count} old entries, kept {len(kept_entries)}.")

def clean_symbol_data_log(file_path="../AI-crypto-trader-logs/analysis-data/symbol_data_log.jsonl", days=30):
    if not os.path.exists(file_path):
        print(f"{os.path.basename(file_path)} not found.")
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
                    print(f"Failed to delete {os.path.basename(fpath)}: {e}")
    if deleted_files:
        print("Deleted temporary log files:")
        for f in deleted_files:
            print(f" - {os.path.basename(f)}")
    else:
        print("No temporary log files found to delete.")

def fix_skipped_orders(input_path, output_path):
    cleaned = []
    with open(input_path, 'r') as f:
        try:
            data = json.load(f)
            print("✅ File is already valid JSON. No fix needed.")
            return
        except json.JSONDecodeError:
            print("⚠️ File is invalid JSON. Attempting to fix...")

    with open(input_path, 'r') as f:
        buffer = ""
        for line in f:
            buffer += line
        try:
            entries = json.loads(buffer)
            # If we get here, the JSON was fixed by reloading
            with open(output_path, 'w') as out:
                json.dump(entries, out, indent=4)
            print(f"✅ Fixed JSON written to {output_path}")
            return
        except json.JSONDecodeError:
            pass

    # Try recovering line-by-line if top-level list
    with open(input_path, 'r') as f:
        print("🔍 Attempting line-by-line recovery...")
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line in ("[", "]", ","):
                continue
            try:
                if line.endswith(","):
                    line = line[:-1]  # remove trailing comma
                entry = json.loads(line)
                cleaned.append(entry)
            except json.JSONDecodeError as e:
                print(f"⚠️ Skipping invalid entry on line {line_num}: {e}")

    with open(output_path, 'w') as f:
        json.dump(cleaned, f, indent=4)
    print(f"✅ Cleaned JSON written to {output_path}, total valid entries: {len(cleaned)}")

def run_log_cleanup():
    archive_complete_signals()
    archive_old_orders()
    remove_old_archives()
    clean_symbol_data_log()
    clean_skipped_orders_log()
    delete_temporary_logs([
        "../AI-crypto-trader-logs/analysis-data/symbol_data_fetcher",
        "../AI-crypto-trader-logs/cron"
    ])

if __name__ == "__main__":
    run_log_cleanup()
