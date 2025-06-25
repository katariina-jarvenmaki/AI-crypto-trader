# signals/log_signal.py

from signals.log_based_signal import get_log_based_signal

def get_log_signal(symbol: str):
    log_signal = get_log_based_signal(symbol)
    highest_bias = None
    hierarchy = ["1w", "1d", "4h", "2h", "1h", "30m", "15m", "5m", "3m", "1m"]

    for tf in hierarchy:
        if tf in log_signal:
            for side in ["buy", "sell"]:
                entry = log_signal[tf].get(side)
                if entry and entry.get("status") != "complete":
                    highest_bias = {"interval": tf, "signal": side}
                    break
        if highest_bias:
            break

    if highest_bias:
        return {"signal": highest_bias["signal"], "interval": highest_bias["interval"]}
    return None
