import json
import os
from datetime import datetime, timedelta

LOG_FILE = "signals_log.json"
SIGNAL_TIMEOUT = timedelta(hours=1)

def load_signal_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_signal_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=4)

def is_signal_allowed(symbol: str, interval: str, signal_type: str, now: datetime) -> bool:
    log = load_signal_log()
    last_time_str = log.get(symbol, {}).get(interval, {}).get(signal_type)
    if last_time_str is None:
        return True
    try:
        last_time = datetime.fromisoformat(last_time_str)
    except ValueError:
        return True
    return now - last_time >= SIGNAL_TIMEOUT

def update_signal_log(symbol: str, interval: str, signal_type: str, now: datetime):
    log = load_signal_log()
    log.setdefault(symbol, {}).setdefault(interval, {})[signal_type] = now.isoformat()
    save_signal_log(log)
