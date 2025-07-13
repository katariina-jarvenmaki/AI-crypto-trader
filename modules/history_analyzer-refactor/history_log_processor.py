# modules/history_analyzer/history_log_processor.py

import os
import json
from typing import List, Dict
from modules.history_analyzer.config_history_analyzer import CONFIG

def process_log_entry(entry: dict):
    symbol = entry["symbol"]
    timestamp = entry["timestamp"]
    history = load_history(symbol)

    # Disable saving duplicates
    if any(e.get("timestamp") == timestamp for e in history):
        print(f"Duplicate entry for symbol={symbol} and timestamp={timestamp}, skipping.")
        return

    last_entry = history[-1] if history else {}

    def get(key): return entry.get(key)
    def prev(key): return last_entry.get(key)

    # Basic data
    current_rsi = get("rsi")
    current_macd = get("macd")
    macd_signal = get("macd_signal")

    # Averages
    avg_rsi_all = average_rsi_1h_4h_1d_1w(current_rsi)
    avg_rsi_1h_4h = average_rsi_1h_4h(current_rsi)
    avg_rsi_1d_1w = average_rsi_1d_1w(current_rsi)

    avg_macd_all = average_macd_1h_4h_1d_1w(current_macd)
    avg_macd_1h_4h = average_macd_1h_4h(current_macd)
    avg_macd_1d_1w = average_macd_1d_1w(current_macd)

    avg_macd_signal_all = average_macd_signal_1h_4h_1d_1w(macd_signal)
    avg_macd_signal_1h_4h = average_macd_signal_1h_4h(macd_signal)
    avg_macd_signal_1d_1w = average_macd_signal_1d_1w(macd_signal)

    # Computed values
    ema_rsi = compute_ema(prev("avg_rsi_all"), avg_rsi_all)
    ema_macd = compute_ema(prev("avg_macd_all"), avg_macd_all)
    ema_macd_signal = compute_ema(prev("avg_macd_signal_all"), avg_macd_signal_all)
    macd_diff = compute_macd_diff(current_macd, macd_signal)

    # New log entry
    new_entry = {
        **{k: get(k) for k in ["timestamp", "symbol", "price", "high_price", "low_price", "volume", "turnover", "change_24h"]},
        "rsi": current_rsi,
        "ema": get("ema"),
        "macd": current_macd,
        "macd_signal": macd_signal,
        "bb_upper": get("bb_upper"),
        "bb_lower": get("bb_lower"),
        "avg_rsi_all": avg_rsi_all,
        "avg_rsi_1h_4h": avg_rsi_1h_4h,
        "avg_rsi_1d_1w": avg_rsi_1d_1w,
        "avg_macd_all": avg_macd_all,
        "avg_macd_1h_4h": avg_macd_1h_4h,
        "avg_macd_1d_1w": avg_macd_1d_1w,
        "avg_macd_signal_all": avg_macd_signal_all,
        "avg_macd_signal_1h_4h": avg_macd_signal_1h_4h,
        "avg_macd_signal_1d_1w": avg_macd_signal_1d_1w,
        "ema_rsi": ema_rsi,
        "ema_macd": ema_macd,
        "ema_macd_signal": ema_macd_signal,
        "macd_diff": macd_diff,
    }

    history.append(new_entry)
    save_history(symbol, history)

def save_history(symbol: str, history: List[dict]):
    filepath = CONFIG["history_log_path"]
    if not history:
        return
    with open(filepath, "a") as f:
        json.dump(history[-1], f)
        f.write("\n")

def history_log_processor(parsed_entries):
    for entry in parsed_entries:
        process_log_entry(entry)

def load_history(symbol: str) -> List[dict]:
    filepath = CONFIG["history_log_path"]
    if not os.path.exists(filepath):
        return []
    history = []
    with open(filepath, "r") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get("symbol") == symbol:
                    history.append(entry)
            except json.JSONDecodeError:
                continue
    return history

def compute_ema(prev_ema: float, current_value: float, alpha=0.1) -> float:
    if prev_ema is None:
        return current_value
    return alpha * current_value + (1 - alpha) * prev_ema

def compute_macd_diff(macd: Dict[str, float], signal: Dict[str, float]) -> float:
    diffs = [
        macd[i] - signal[i]
        for i in CONFIG["intervals_to_use"]
        if isinstance(macd.get(i), (int, float)) and isinstance(signal.get(i), (int, float))
    ]
    return sum(diffs) / len(diffs) if diffs else None

def average_rsi_1h_4h_1d_1w(rsi_dict):
    keys = ['1h', '4h', '1d', '1w']
    values = [rsi_dict.get(k) for k in keys if rsi_dict.get(k) is not None]
    if not values:
        return None
    return sum(values) / len(values)

def average_rsi_1h_4h(rsi_dict):
    keys = ['1h', '4h']
    values = [rsi_dict.get(k) for k in keys if rsi_dict.get(k) is not None]
    if not values:
        return None
    return sum(values) / len(values)

def average_rsi_1d_1w(rsi_dict):
    keys = ['1d', '1w']
    values = [rsi_dict.get(k) for k in keys if rsi_dict.get(k) is not None]
    if not values:
        return None
    return sum(values) / len(values)

def average_macd_1h_4h_1d_1w(macd: dict) -> float:
    values = [macd.get(k) for k in ['1h', '4h', '1d', '1w'] if macd.get(k) is not None]
    if not values:
        return None
    return sum(values) / len(values)

def average_macd_1h_4h(macd: dict) -> float:
    values = [macd.get(k) for k in ['1h', '4h'] if macd.get(k) is not None]
    if not values:
        return None
    return sum(values) / len(values)

def average_macd_1d_1w(macd: dict) -> float:
    values = [macd.get(k) for k in ['1d', '1w'] if macd.get(k) is not None]
    if not values:
        return None
    return sum(values) / len(values)

def average_macd_signal_1h_4h_1d_1w(macd_signal: dict) -> float:
    values = [macd_signal.get(k) for k in ['1h', '4h', '1d', '1w'] if macd_signal.get(k) is not None]
    if not values:
        return None
    return sum(values) / len(values)

def average_macd_signal_1h_4h(macd_signal: dict) -> float:
    values = [macd_signal.get(k) for k in ['1h', '4h'] if macd_signal.get(k) is not None]
    if not values:
        return None
    return sum(values) / len(values)

def average_macd_signal_1d_1w(macd_signal: dict) -> float:
    values = [macd_signal.get(k) for k in ['1d', '1w'] if macd_signal.get(k) is not None]
    if not values:
        return None
    return sum(values) / len(values)
