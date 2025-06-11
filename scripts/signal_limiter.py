import json
import os
from datetime import datetime
from configs.config import LOG_FILE, SIGNAL_TIMEOUT

def load_signal_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                data = json.load(f)
                if not isinstance(data, dict):
                    return {}
                return data
            except json.JSONDecodeError:
                return {}
    return {}

def save_signal_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=4)

def is_signal_allowed(symbol: str, interval: str, signal_type: str, now: datetime, mode: str = "default") -> bool:
    log = load_signal_log()
    last_time_str = (
        log.get(symbol, {})
           .get(interval, {})
           .get(signal_type, {})
           .get(mode)
    )

    if last_time_str is None:
        last_time_str = (
            log.get(symbol, {})
               .get(interval, {})
               .get(signal_type)
        )
        if isinstance(last_time_str, dict):
            return True

    if last_time_str is None:
        return True

    try:
        last_time = datetime.fromisoformat(last_time_str)
        if last_time.tzinfo is None:
            from pytz import UTC
            last_time = last_time.replace(tzinfo=UTC)
    except ValueError:
        return True

    return now - last_time >= SIGNAL_TIMEOUT

def update_signal_log(symbol: str, interval: str, signal_type: str, now: datetime, mode: str = "default", market_info: dict = None):
    log = load_signal_log()
    signal_entry = log.setdefault(symbol, {}) \
                      .setdefault(interval, {}) \
                      .setdefault(signal_type, {})

    signal_entry[mode] = now.isoformat()

    if market_info:
        signal_entry["market_state"] = market_info.get("state")
        signal_entry["started_on"] = market_info.get("started_on")

    save_signal_log(log)
