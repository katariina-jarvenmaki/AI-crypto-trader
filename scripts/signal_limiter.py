# scripts/signal_limiter.py

import json
import os
from datetime import datetime
from pytz import UTC
from configs.config import LOG_FILE, SIGNAL_TIMEOUT, TIMEZONE

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
    # Varmista että now on oikeassa aikavyöhykkeessä
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC).astimezone(TIMEZONE)
    else:
        now = now.astimezone(TIMEZONE)

    log = load_signal_log()

    signal_entry = (
        log.get(symbol, {})
           .get(interval, {})
           .get(signal_type, {})
    )

    # If no entry -> accept signal
    if not signal_entry:
        return True

    entry_for_mode = signal_entry.get(mode)

    # If no entry mode -> accept signal
    if not entry_for_mode:
        return True

    # Check for old format
    if isinstance(entry_for_mode, str):
        try:
            last_time = datetime.fromisoformat(entry_for_mode)
            if last_time.tzinfo is None:
                last_time = last_time.replace(tzinfo=UTC).astimezone(TIMEZONE)
            else:
                last_time = last_time.astimezone(TIMEZONE)
            return now - last_time >= SIGNAL_TIMEOUT
        except ValueError:
            return True

    # If status is complete, accept signal
    if entry_for_mode.get("status") == "complete":
        return True

    # Check the timestamp
    time_str = entry_for_mode.get("time") or entry_for_mode.get("rsi") or entry_for_mode.get("timestamp") or entry_for_mode.get("datetime")
    if not time_str:
        return True

    try:
        last_time = datetime.fromisoformat(time_str)
        if last_time.tzinfo is None:
            last_time = last_time.replace(tzinfo=UTC).astimezone(TIMEZONE)
        else:
            last_time = last_time.astimezone(TIMEZONE)
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
    momentum_strength: str = None,
    status: str = None,
    price_change: str = None,
    volume_multiplier: float = None
):
    # Varmista että now on oikeassa aikavyöhykkeessä
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC).astimezone(TIMEZONE)
    else:
        now = now.astimezone(TIMEZONE)

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
    if status:
        signal_entry["status"] = status

    # 🔍 Search for any different previous state
    previous_state = None
    for _interval_data in log.get(symbol, {}).values():
        for _signal_data in _interval_data.values():
            if isinstance(_signal_data, dict):
                logged_state = _signal_data.get("market_state")
                if logged_state and market_state and logged_state != market_state:
                    previous_state = logged_state

    if previous_state:
        signal_entry["previous_market_state"] = previous_state

    save_signal_log(log)
