# signals/log_signal.py

from signals.log_based_signal import get_log_based_signal

def get_log_signal(symbol: str):
    log_signal = get_log_based_signal(symbol)
    if not log_signal:
        return None
    return {
        "signal": log_signal.get("signal"),
        "interval": log_signal.get("interval"),
        "mode": log_signal.get("mode"),
    }
