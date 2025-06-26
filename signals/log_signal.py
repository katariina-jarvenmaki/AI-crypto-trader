# signals/log_signal.py

from signals.log_based_signal import get_log_based_signal

def get_log_signal(symbol: str, signal_type: str = None):
    log_signal = get_log_based_signal(symbol, signal_type)
    if not log_signal:
        return None
    return {
        "signal": log_signal.get("signal"),
        "interval": log_signal.get("interval"),
        "mode": log_signal.get("mode"),
    }
