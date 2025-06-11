# scripts/signal_limiter.py
import json
import os
from datetime import datetime
from configs.config import LOG_FILE, SIGNAL_TIMEOUT

# Load the signal log
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

# Save to signal log
def save_signal_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=4)

# Check if signal is allowed to let through (used in rsi_analyzer.py)
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

# Make a new record to log
def update_signal_log(
    symbol: str,
    interval: str,
    signal_type: str,
    now: datetime,
    mode: str = "default",
    market_state: str = None,
    started_on: str = None,
    momentum_strength: str = None
):
    log = load_signal_log()

    signal_entry = log.setdefault(symbol, {}) \
                      .setdefault(interval, {}) \
                      .setdefault(signal_type, {})

    signal_entry[mode] = now.isoformat()

    if market_state:
        signal_entry["market_state"] = market_state
    if started_on:
        signal_entry["started_on"] = started_on
    if momentum_strength:
        signal_entry["momentum_strength"] = momentum_strength 

    # 🔍 Search for any different previous state
    previous_state = None
    for _interval_data in log.get(symbol, {}).values():
        for _signal_data in _interval_data.values():
            if isinstance(_signal_data, dict):
                logged_state = _signal_data.get("market_state")
                if logged_state and logged_state != market_state:
                    previous_state = logged_state
    if previous_state:
        signal_entry["previous_market_state"] = previous_state

    save_signal_log(log)