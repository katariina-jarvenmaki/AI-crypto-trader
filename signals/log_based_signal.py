# signals/log_based_signal.py
from configs.config import TIMEZONE, LOG_BASED_SIGNAL_TIMEOUT
from scripts.signal_limiter import load_signal_log
from datetime import datetime, timedelta
import pytz

def get_log_based_signal(symbol: str) -> dict:
    log = load_signal_log()
    now = datetime.now(pytz.timezone(TIMEZONE.zone))
    symbol_log = log.get(symbol, {})

    if not symbol_log:
        return {}

    valid_entries = []

    for interval, signals in symbol_log.items():
        for signal_type in ['buy', 'sell']:
            entry = signals.get(signal_type)
            if not entry or not isinstance(entry, dict):
                continue

            # If status is "complete" ignore
            if entry.get("status") == "complete":
                continue

            # Check timestamp
            time_str = entry.get("time") or entry.get("rsi") or entry.get("timestamp") or entry.get("datetime")
            if not time_str:
                continue

            try:
                ts = datetime.fromisoformat(time_str)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(TIMEZONE.zone))
            except ValueError:
                continue

            # Check, if is new enough
            if now - ts > LOG_BASED_SIGNAL_TIMEOUT:
                continue

            print(f"Valid log entry found for {symbol}: interval={interval}, signal={signal_type}, time={ts.isoformat()}")

            valid_entries.append({
                "signal": signal_type,
                "interval": interval,
                "time": ts
            })

    if not valid_entries:
        return {}

    # Järjestetään ensin intervalli-pituuden ja sitten ajan mukaan
    def interval_sort_key(entry):
        unit_weight = {"m": 1, "h": 60, "d": 1440}
        try:
            num = int(''.join(filter(str.isdigit, entry["interval"])))
            unit = ''.join(filter(str.isalpha, entry["interval"]))
            return (unit_weight.get(unit, 1) * num, entry["time"].timestamp())
        except:
            return (0, entry["time"].timestamp())

    best_entry = sorted(valid_entries, key=interval_sort_key, reverse=True)[0]

    return {
        "signal": best_entry["signal"],
        "interval": best_entry["interval"],
        "mode": "log"
    }
