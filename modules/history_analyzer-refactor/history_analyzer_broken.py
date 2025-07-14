OLD:


# modules/history_analyzer/history_analyzer.py

import os
import json
import math
from collections import defaultdict
from dateutil.parser import isoparse
from typing import List, Dict, Tuple
from datetime import datetime, timedelta, timezone
from modules.history_analyzer.config_history_analyzer import CONFIG

def process_log_entry(entry: dict):

    ...

    divergence = detect_rsi_divergence(history, avg_rsi)
    delta = abs(avg_rsi - prev_avg) if prev_avg is not None else None

    if delta is not None and delta < CONFIG["rsi_change_threshold"]:
        return

    flag = detect_flag(prev_avg, avg_rsi) if prev_avg is not None else "neutral"

    if macd_diff is not None and abs(macd_diff) > CONFIG["macd_diff_threshold"]:
        macd_trend = "bullish" if macd_diff > 0 else "bearish"
    else:
        macd_trend = "neutral"

    price_trend = detect_price_trend(last_entry.get("price") if last_entry else None, price)
    volume_class = classify_volume(volume)
    change_class = interpret_change_24h(change_24h)

    new_entry = {
        "timestamp": timestamp,
        "symbol": symbol,
        "price": price,
        "price_trend": price_trend,
        "volume": volume,
        "volume_class": volume_class,
        "change_24h": change_24h,
        "change_class": change_class,
        "rsi": current_rsi,
        "avg_rsi": avg_rsi,
        "avg_rsi_1h_4h": avg_rsi_1h_4h_val,
        "avg_rsi_1d_1w": avg_rsi_1d_1w_val,
        "ema_rsi": ema_rsi,
        "macd": macd,
        "macd_signal_raw": macd_signal,
        "macd_diff": macd_diff,
        "macd_signal": macd_trend,
        "avg_macd_all": avg_macd_all,
        "avg_macd_1h_4h": avg_macd_1h_4h_val,
        "avg_macd_1d_1w": avg_macd_1d_1w_val,
        "ema_macd": ema_macd,
        "avg_macd_signal_all": avg_macd_signal_all,
        "avg_macd_signal_1h_4h": avg_macd_signal_1h_4h_val,
        "avg_macd_signal_1d_1w": avg_macd_signal_1d_1w_val,
        "ema_macd_signal": ema_macd_signal,
        "rsi_divergence": divergence,
        "flag": flag,
        "prev_avg_rsi": prev_avg,
        "delta": delta,
        "prev_ema_rsi": prev_ema_rsi,
        "prev_ema_macd": prev_ema_macd,
        "prev_ema_macd_signal": prev_ema_macd_signal
    }

    history.append(new_entry)
    save_history(symbol, history)

    print(f"""
✅ FINAL ANALYSIS for {symbol} @ {timestamp}
- price: {price} ({price_trend})
- volume: {volume} ({volume_class})
- 24h change: {change_24h}% ({change_class})
- avg_rsi: {avg_rsi}
- ema_rsi: {ema_rsi}
- avg_macd_all: {avg_macd_all}
- ema_macd: {ema_macd}
- avg_macd_signal_all: {avg_macd_signal_all}
- ema_macd_signal: {ema_macd_signal}
- macd_diff: {macd_diff}
- rsi_divergence: {divergence}
- flag: {flag}
- macd_trend: {macd_trend}
""")

def interpret_change_24h(change: float) -> str:
    if change is None:
        return "unknown"
    if change > 5:
        return "strong-up"
    elif change > 0:
        return "mild-up"
    elif change < -5:
        return "strong-down"
    elif change < 0:
        return "mild-down"
    return "neutral"

def detect_flag(prev_avg: float, current_avg: float) -> str:
    if current_avg > prev_avg:
        return "bull-flag"
    elif current_avg < prev_avg:
        return "bear-flag"
    return "neutral"

def detect_price_trend(prev_price: float, current_price: float) -> str:
    if prev_price is None:
        return "neutral"
    if current_price > prev_price:
        return "price-up"
    elif current_price < prev_price:
        return "price-down"
    return "neutral"

def classify_volume(volume: float) -> str:
    if volume is None:
        return "unknown"
    if volume > 1_000_000:
        return "high-volume"
    elif volume > 100_000:
        return "medium-volume"
    return "low-volume"

def detect_rsi_divergence(history: List[Dict], current_avg: float) -> str:
    if len(history) < CONFIG["rsi_divergence_window"]:
        return "none"
    prev = history[-1]
    prev2 = history[-2]
    if prev["avg_rsi"] > prev2["avg_rsi"] and current_avg < prev["avg_rsi"]:
        return "bearish-divergence"
    elif prev["avg_rsi"] < prev2["avg_rsi"] and current_avg > prev["avg_rsi"]:
        return "bullish-divergence"
    return "none"

def convert_price_log_entry_to_ohlcv_format(entry):
    """
    Convert price_data_log.jsonl format into a format expected by process_log_entry
    """
    symbol = entry.get("symbol")
    timestamp = entry.get("timestamp")
    data_preview = {
        "1m": {
            "close": entry["data_preview"].get("last_price")
        },
        "1d": {
            "volume": entry["data_preview"].get("volume"),
            "change_24h": entry["data_preview"].get("price_change_percent")
        }
    }

    return {
        "symbol": symbol,
        "timestamp": timestamp,
        "data_preview": data_preview
    }





    
    
 ---------------   
    
    
    def process_log_entry(entry: dict):

    ...

    # Bollinger-analyysi
    def analyze_bollinger(price, bb_upper, bb_lower):
        if price >= bb_upper:
            return "overbought"
        elif price <= bb_lower:
            return "oversold"
        return "neutral"

    bollinger_status = analyze_bollinger(price, bb_upper["1d"], bb_lower["1d"])

    # EMA vs Price
    def detect_ema_trend(price, ema_1d):
        if price > ema_1d * 1.01:
            return "strong_above"
        elif price < ema_1d * 0.99:
            return "strong_below"
        return "near_ema"

    ema_trend = detect_ema_trend(price, ema["1d"])

    # Turnover analyysi
    def detect_turnover_anomaly(turnover, volume, price):
        if volume == 0:
            return "invalid"
        avg_price = turnover / volume
        deviation = abs(avg_price - price) / price
        return "mismatch" if deviation > 0.02 else "normal"

    turnover_status = detect_turnover_anomaly(turnover, volume, price)

    # RSI divergence
    rsi_divergence = detect_rsi_divergence(history, avg_rsi)
    delta_rsi = abs(avg_rsi - prev_avg_rsi) if prev_avg_rsi is not None else None

    if delta_rsi is not None and delta_rsi < CONFIG["rsi_change_threshold"]:
        return  # Ei riittävästi muutosta

    flag = detect_flag(prev_avg_rsi, avg_rsi) if prev_avg_rsi else "neutral"

    # MACD trendin suunta
    macd_trend = "neutral"
    if macd_diff is not None and abs(macd_diff) > CONFIG["macd_diff_threshold"]:
        macd_trend = "bullish" if macd_diff > 0 else "bearish"

    price_trend = detect_price_trend(last_entry.get("price"), price)
    volume_class = classify_volume(volume)
    change_class = interpret_change_24h(change_24h)

    # Signaalin vahvuuden arviointi
    def estimate_signal_strength(flag, macd_trend, bollinger_status, rsi_divergence, ema_trend):
        if flag == "bullish" and macd_trend == "bullish" and bollinger_status == "oversold" and ema_trend == "strong_above":
            return "very_strong_bullish"
        if flag == "bearish" and macd_trend == "bearish" and bollinger_status == "overbought" and ema_trend == "strong_below":
            return "very_strong_bearish"
        if rsi_divergence:
            return "watch_for_reversal"
        return "neutral"

    signal_strength = estimate_signal_strength(flag, macd_trend, bollinger_status, rsi_divergence, ema_trend)

    new_entry = {
        "timestamp": timestamp,
        "symbol": symbol,
        "price": price,
        "price_trend": price_trend,
        "volume": volume,
        "volume_class": volume_class,
        "change_24h": change_24h,
        "change_class": change_class,
        "rsi": rsi,
        "avg_rsi": avg_rsi,
        "ema_rsi": ema_rsi,
        "macd": macd,
        "macd_signal": macd_signal,
        "macd_diff": macd_diff,
        "ema_macd": ema_macd,
        "ema_macd_signal": ema_macd_signal,
        "rsi_divergence": rsi_divergence,
        "flag": flag,
        "macd_trend": macd_trend,
        "bollinger_status": bollinger_status,
        "ema_trend": ema_trend,
        "turnover_status": turnover_status,
        "signal_strength": signal_strength,
        "prev_avg_rsi": prev_avg_rsi,
        "delta_rsi": delta_rsi
    }

    history.append(new_entry)
    save_history(symbol, history)

    print(f"""
✅ FINAL ANALYSIS for {symbol} @ {timestamp}
- price: {price} ({price_trend})
- volume: {volume} ({volume_class})
- 24h change: {change_24h}% ({change_class})
- avg_rsi: {avg_rsi}, ema_rsi: {ema_rsi}
- macd_diff: {macd_diff}, trend: {macd_trend}
- bollinger: {bollinger_status}, ema_trend: {ema_trend}
- turnover check: {turnover_status}
- RSI divergence: {rsi_divergence}, flag: {flag}
- 🔥 signal_strength: {signal_strength}
""")





from modules.history_analyzer.data_collector import parse_log_entry
from modules.history_analyzer.indicators import (
    average_rsi_1h_4h_1d_1w, average_rsi_1h_4h, average_rsi_1d_1w,
    average_macd_1h_4h_1d_1w, average_macd_1h_4h, average_macd_1d_1w,
    average_macd_signal_1h_4h_1d_1w, average_macd_signal_1h_4h, average_macd_signal_1d_1w,
    compute_ema, compute_macd_diff
)
from modules.history_analyzer.utils import (
    load_history, save_history, detect_rsi_divergence, detect_flag,
    detect_price_trend, classify_volume, interpret_change_24h
)
from modules.history_analyzer.config_history_analyzer import CONFIG


def process_log_entry(entry: dict):
    parsed = parse_log_entry(entry)
    symbol = parsed["symbol"]
    timestamp = parsed["timestamp"]
    price = parsed["price"]
    volume = parsed["volume"]
    change_24h = parsed["change_24h"]
    current_rsi = parsed["rsi"]
    macd = parsed["macd"]
    macd_signal = parsed["macd_signal"]

    avg_rsi_all = average_rsi_1h_4h_1d_1w(current_rsi)
    avg_rsi_1h_4h_val = average_rsi_1h_4h(current_rsi)
    avg_rsi_1d_1w_val = average_rsi_1d_1w(current_rsi)

    avg_macd_all = average_macd_1h_4h_1d_1w(macd)
    avg_macd_1h_4h_val = average_macd_1h_4h(macd)
    avg_macd_1d_1w_val = average_macd_1d_1w(macd)

    avg_macd_signal_all = average_macd_signal_1h_4h_1d_1w(macd_signal)
    avg_macd_signal_1h_4h_val = average_macd_signal_1h_4h(macd_signal)
    avg_macd_signal_1d_1w_val = average_macd_signal_1d_1w(macd_signal)

    history = load_history(symbol)
    last_entry = history[-1] if history else {}

    prev_avg = last_entry.get("avg_rsi")
    prev_ema_rsi = last_entry.get("ema_rsi")
    ema_rsi = compute_ema(prev_ema_rsi, avg_rsi_all)

    prev_ema_macd = last_entry.get("ema_macd")
    prev_ema_macd_signal = last_entry.get("ema_macd_signal")

    ema_macd = compute_ema(prev_ema_macd, avg_macd_all)
    ema_macd_signal = compute_ema(prev_ema_macd_signal, avg_macd_signal_all)

    macd_diff = compute_macd_diff(macd, macd_signal)
    divergence = detect_rsi_divergence(history, avg_rsi_all)
    delta = abs(avg_rsi_all - prev_avg) if prev_avg is not None else None

    if delta is not None and delta < CONFIG["rsi_change_threshold"]:
        return

    flag = detect_flag(prev_avg, avg_rsi_all) if prev_avg is not None else "neutral"

    macd_trend = "neutral"
    if macd_diff is not None and abs(macd_diff) > CONFIG["macd_diff_threshold"]:
        macd_trend = "bullish" if macd_diff > 0 else "bearish"

    price_trend = detect_price_trend(last_entry.get("price"), price)
    volume_class = classify_volume(volume)
    change_class = interpret_change_24h(change_24h)

    new_entry = {
        "timestamp": timestamp,
        "symbol": symbol,
        "price": price,
        "price_trend": price_trend,
        "volume": volume,
        "volume_class": volume_class,
        "change_24h": change_24h,
        "change_class": change_class,
        "rsi": current_rsi,
        "avg_rsi": avg_rsi_all,
        "avg_rsi_1h_4h": avg_rsi_1h_4h_val,
        "avg_rsi_1d_1w": avg_rsi_1d_1w_val,
        "ema_rsi": ema_rsi,
        "macd": macd,
        "macd_signal_raw": macd_signal,
        "macd_diff": macd_diff,
        "macd_signal": macd_trend,
        "avg_macd_all": avg_macd_all,
        "avg_macd_1h_4h": avg_macd_1h_4h_val,
        "avg_macd_1d_1w": avg_macd_1d_1w_val,
        "ema_macd": ema_macd,
        "avg_macd_signal_all": avg_macd_signal_all,
        "avg_macd_signal_1h_4h": avg_macd_signal_1h_4h_val,
        "avg_macd_signal_1d_1w": avg_macd_signal_1d_1w_val,
        "ema_macd_signal": ema_macd_signal,
        "rsi_divergence": divergence,
        "flag": flag,
        "prev_avg_rsi": prev_avg,
        "delta": delta,
        "prev_ema_rsi": prev_ema_rsi,
        "prev_ema_macd": prev_ema_macd,
        "prev_ema_macd_signal": prev_ema_macd_signal
    }

    history.append(new_entry)
    save_history(symbol, history)

    print(f"""
✅ FINAL ANALYSIS for {symbol} @ {timestamp}
- price: {price} ({price_trend})
- volume: {volume} ({volume_class})
- 24h change: {change_24h}% ({change_class})
- avg_rsi: {avg_rsi_all}
- ema_rsi: {ema_rsi}
- avg_macd_all: {avg_macd_all}
- ema_macd: {ema_macd}
- avg_macd_signal_all: {avg_macd_signal_all}
- ema_macd_signal: {ema_macd_signal}
- macd_diff: {macd_diff}
- rsi_divergence: {divergence}
- flag: {flag}
- macd_trend: {macd_trend}
""")


# modules/history_analyzer/history_analyzer.py

import os
import json
import math
from collections import defaultdict
from dateutil.parser import isoparse
from typing import List, Dict, Tuple
from datetime import datetime, timedelta, timezone
from modules.history_analyzer.config_history_analyzer import CONFIG

def process_log_entry(entry: dict):
    parsed = parse_log_entry(entry)
    print(f"Parsed: {parsed}")
    symbol = parsed["symbol"]
    timestamp = parsed["timestamp"]
    price = parsed["price"]
    volume = parsed["volume"]
    change_24h = parsed["change_24h"]
    current_rsi = parsed["rsi"]
    macd = parsed["macd"]
    macd_signal = parsed["macd_signal"]

    # RSI keskiarvot
    avg_rsi_all = average_rsi_1h_4h_1d_1w(current_rsi)
    avg_rsi_1h_4h_val = average_rsi_1h_4h(current_rsi)
    avg_rsi_1d_1w_val = average_rsi_1d_1w(current_rsi)

    # MACD keskiarvot
    avg_macd_all = average_macd_1h_4h_1d_1w(macd)
    avg_macd_1h_4h_val = average_macd_1h_4h(macd)
    avg_macd_1d_1w_val = average_macd_1d_1w(macd)

    # MACD signal keskiarvot
    avg_macd_signal_all = average_macd_signal_1h_4h_1d_1w(macd_signal)
    avg_macd_signal_1h_4h_val = average_macd_signal_1h_4h(macd_signal)
    avg_macd_signal_1d_1w_val = average_macd_signal_1d_1w(macd_signal)

    history = load_history(symbol)
    last_entry = history[-1] if history else None

    avg_rsi = avg_rsi_all
    prev_avg = last_entry.get("avg_rsi") if last_entry else None
    prev_ema_rsi = last_entry.get("ema_rsi") if last_entry else None

    # EMA RSI
    ema_rsi = compute_ema(prev_ema_rsi, avg_rsi)

    # EMA MACD ja MACD signal
    prev_ema_macd = last_entry.get("ema_macd") if last_entry else None
    prev_ema_macd_signal = last_entry.get("ema_macd_signal") if last_entry else None

    ema_macd = compute_ema(prev_ema_macd, avg_macd_all)
    ema_macd_signal = compute_ema(prev_ema_macd_signal, avg_macd_signal_all)

    macd_diff = compute_macd_diff(macd, macd_signal)
    divergence = detect_rsi_divergence(history, avg_rsi)
    delta = abs(avg_rsi - prev_avg) if prev_avg is not None else None

    if delta is not None and delta < CONFIG["rsi_change_threshold"]:
        return

    flag = detect_flag(prev_avg, avg_rsi) if prev_avg is not None else "neutral"

    if macd_diff is not None and abs(macd_diff) > CONFIG["macd_diff_threshold"]:
        macd_trend = "bullish" if macd_diff > 0 else "bearish"
    else:
        macd_trend = "neutral"

    price_trend = detect_price_trend(last_entry.get("price") if last_entry else None, price)
    volume_class = classify_volume(volume)
    change_class = interpret_change_24h(change_24h)

    new_entry = {
        "timestamp": timestamp,
        "symbol": symbol,
        "price": price,
        "price_trend": price_trend,
        "volume": volume,
        "volume_class": volume_class,
        "change_24h": change_24h,
        "change_class": change_class,
        "rsi": current_rsi,
        "avg_rsi": avg_rsi,
        "avg_rsi_1h_4h": avg_rsi_1h_4h_val,
        "avg_rsi_1d_1w": avg_rsi_1d_1w_val,
        "ema_rsi": ema_rsi,
        "macd": macd,
        "macd_signal_raw": macd_signal,
        "macd_diff": macd_diff,
        "macd_signal": macd_trend,
        "avg_macd_all": avg_macd_all,
        "avg_macd_1h_4h": avg_macd_1h_4h_val,
        "avg_macd_1d_1w": avg_macd_1d_1w_val,
        "ema_macd": ema_macd,
        "avg_macd_signal_all": avg_macd_signal_all,
        "avg_macd_signal_1h_4h": avg_macd_signal_1h_4h_val,
        "avg_macd_signal_1d_1w": avg_macd_signal_1d_1w_val,
        "ema_macd_signal": ema_macd_signal,
        "rsi_divergence": divergence,
        "flag": flag,
        "prev_avg_rsi": prev_avg,
        "delta": delta,
        "prev_ema_rsi": prev_ema_rsi,
        "prev_ema_macd": prev_ema_macd,
        "prev_ema_macd_signal": prev_ema_macd_signal
    }

    history.append(new_entry)
    save_history(symbol, history)

    print(f"""
✅ FINAL ANALYSIS for {symbol} @ {timestamp}
- price: {price} ({price_trend})
- volume: {volume} ({volume_class})
- 24h change: {change_24h}% ({change_class})
- avg_rsi: {avg_rsi}
- ema_rsi: {ema_rsi}
- avg_macd_all: {avg_macd_all}
- ema_macd: {ema_macd}
- avg_macd_signal_all: {avg_macd_signal_all}
- ema_macd_signal: {ema_macd_signal}
- macd_diff: {macd_diff}
- rsi_divergence: {divergence}
- flag: {flag}
- macd_trend: {macd_trend}
""")

def save_history(symbol: str, history: List[dict]):
    filepath = CONFIG["history_log_path"]
    if not history:
        return
    with open(filepath, "a") as f:
        json.dump(history[-1], f)
        f.write("\n")



def interpret_change_24h(change: float) -> str:
    if change is None:
        return "unknown"
    if change > 5:
        return "strong-up"
    elif change > 0:
        return "mild-up"
    elif change < -5:
        return "strong-down"
    elif change < 0:
        return "mild-down"
    return "neutral"

def detect_flag(prev_avg: float, current_avg: float) -> str:
    if current_avg > prev_avg:
        return "bull-flag"
    elif current_avg < prev_avg:
        return "bear-flag"
    return "neutral"

def detect_price_trend(prev_price: float, current_price: float) -> str:
    if prev_price is None:
        return "neutral"
    if current_price > prev_price:
        return "price-up"
    elif current_price < prev_price:
        return "price-down"
    return "neutral"

def classify_volume(volume: float) -> str:
    if volume is None:
        return "unknown"
    if volume > 1_000_000:
        return "high-volume"
    elif volume > 100_000:
        return "medium-volume"
    return "low-volume"

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

def detect_rsi_divergence(history: List[Dict], current_avg: float) -> str:
    if len(history) < CONFIG["rsi_divergence_window"]:
        return "none"
    prev = history[-1]
    prev2 = history[-2]
    if prev["avg_rsi"] > prev2["avg_rsi"] and current_avg < prev["avg_rsi"]:
        return "bearish-divergence"
    elif prev["avg_rsi"] < prev2["avg_rsi"] and current_avg > prev["avg_rsi"]:
        return "bullish-divergence"
    return "none"

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

def convert_price_log_entry_to_ohlcv_format(entry):
    """
    Convert price_data_log.jsonl format into a format expected by process_log_entry
    """
    symbol = entry.get("symbol")
    timestamp = entry.get("timestamp")
    data_preview = {
        "1m": {
            "close": entry["data_preview"].get("last_price")
        },
        "1d": {
            "volume": entry["data_preview"].get("volume"),
            "change_24h": entry["data_preview"].get("price_change_percent")
        }
    }

    return {
        "symbol": symbol,
        "timestamp": timestamp,
        "data_preview": data_preview
    }

def ensure_previous_day_log_file_exists(logs_path: str) -> str:
    yesterday = datetime.now() - timedelta(days=1)
    filename = f"history_data_log_day_{yesterday.strftime('%d_%m_%Y')}.jsonl"
    log_file_path = os.path.join(logs_path, filename)
    if not os.path.exists(log_file_path):
        open(log_file_path, "w").close()
    return log_file_path

def read_entries_for_date(file_path: str, date_str: str) -> List[dict]:
    results = []
    with open(file_path, "r") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                timestamp = entry.get("timestamp")
                if timestamp and timestamp.startswith(date_str):
                    results.append(entry)
            except json.JSONDecodeError:
                continue
    return results

def write_entries_to_file(entries: List[dict], target_file: str):
    with open(target_file, "a") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

def retain_last_entry_per_hour_per_symbol(entries: List[dict]) -> List[dict]:
    latest_entries: Dict[Tuple[str, str], dict] = {}

    for entry in entries:
        ts_str = entry.get("timestamp")
        symbol = entry.get("symbol")
        if not ts_str or not symbol:
            continue

        try:
            ts_dt = isoparse(ts_str)  # Säilytä alkuperäinen aikavyöhyke
            hour_key = ts_dt.strftime("%Y-%m-%dT%H")  # esim. "2025-07-11T17"
            key = (symbol, hour_key)

            if key not in latest_entries or ts_dt > isoparse(latest_entries[key]["timestamp"]):
                latest_entries[key] = entry

        except Exception as e:
            continue  # virheelliset timestampit ohitetaan

    return list(latest_entries.values())

def rewrite_log_without_old_entries(source_file: str, date_str: str, retained_entries: List[dict]):
    new_lines = []
    retained_keys = {(e["symbol"], e["timestamp"]) for e in retained_entries}

    with open(source_file, "r") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                ts = entry.get("timestamp", "")
                symbol = entry.get("symbol", "")
                if ts.startswith(date_str):
                    if (symbol, ts) in retained_keys:
                        new_lines.append(json.dumps(entry))
                else:
                    new_lines.append(json.dumps(entry))
            except json.JSONDecodeError:
                continue

    with open(source_file, "w") as f:
        for line in new_lines:
            f.write(line + "\n")

def archive_previous_day_logs():
    logs_path = CONFIG["daily_logs_path"]
    history_log_path = CONFIG["history_log_path"]

    yesterday_dt = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday_dt.strftime("%Y-%m-%d")

    daily_log_file = ensure_previous_day_log_file_exists(logs_path)
    yesterdays_entries = read_entries_for_date(history_log_path, yesterday_str)

    if not yesterdays_entries:
        print(f"No entries found for {yesterday_str}")
        return

    write_entries_to_file(yesterdays_entries, daily_log_file)

    retained = retain_last_entry_per_hour_per_symbol(yesterdays_entries)
    rewrite_log_without_old_entries(history_log_path, yesterday_str, retained)

    print(f"✔ Archived {len(yesterdays_entries)} entries to {daily_log_file}")
    print(f"✔ Cleaned to {len(retained)} hourly last entries per symbol")

def retain_last_entry_per_hour_per_symbol_debug(entries):
    latest_entries = {}

    for entry in entries:
        ts_str = entry.get("timestamp")
        symbol = entry.get("symbol")
        if not ts_str or not symbol:
            continue

        try:
            ts_dt = isoparse(ts_str)
            hour_key = ts_dt.strftime("%Y-%m-%dT%H")
            key = (symbol, hour_key)

            if key not in latest_entries:
                latest_entries[key] = entry
                print(f"Lisätään uusi avain {key} timestamp: {ts_str}")
            else:
                existing_ts = isoparse(latest_entries[key]["timestamp"])
                print(f"Vertailen {ts_str} (uusi) vs {existing_ts.isoformat()} (vanha) avaimella {key}")
                if ts_dt > existing_ts:
                    print(f"Korvataan vanha kirjauksella {ts_str}")
                    latest_entries[key] = entry
                else:
                    print("Vanha säilyy")

        except Exception as e:
            print(f"Virhe aikaleiman käsittelyssä: {e}")
            continue

    return list(latest_entries.values())

def main():

    archive_previous_day_logs()
    symbols = get_latest_symbols_from_log(CONFIG["symbol_log_path"])

    if not symbols:
        print("No symbols found in latest symbol log.")
        return

    print(f"Found {len(symbols)} symbols to process...")
    process_latest_entries_for_symbols(symbols)

if __name__ == "__main__":
    main()









ChatGPT-ehdotus:

def process_log_entry(entry: dict):

    bollinger_status = analyze_bollinger(price, bb_upper["1d"], bb_lower["1d"])

    ema_trend = detect_ema_trend(price, ema["1d"])

    turnover_status = detect_turnover_anomaly(turnover, volume, price)

    # RSI divergence
    rsi_divergence = detect_rsi_divergence(history, avg_rsi)
    delta_rsi = abs(avg_rsi - prev_avg_rsi) if prev_avg_rsi is not None else None

    if delta_rsi is not None and delta_rsi < CONFIG["rsi_change_threshold"]:
        return  # Ei riittävästi muutosta

    flag = detect_flag(prev_avg_rsi, avg_rsi) if prev_avg_rsi else "neutral"

    # MACD trendin suunta
    macd_trend = "neutral"
    if macd_diff is not None and abs(macd_diff) > CONFIG["macd_diff_threshold"]:
        macd_trend = "bullish" if macd_diff > 0 else "bearish"

    price_trend = detect_price_trend(last_entry.get("price"), price)
    volume_class = classify_volume(volume)
    change_class = interpret_change_24h(change_24h)

    signal_strength = estimate_signal_strength(flag, macd_trend, bollinger_status, rsi_divergence, ema_trend)

    new_entry = {
        "timestamp": timestamp,
        "symbol": symbol,
        "price": price,
        "price_trend": price_trend,
        "volume": volume,
        "volume_class": volume_class,
        "change_24h": change_24h,
        "change_class": change_class,
        "rsi": rsi,
        "avg_rsi": avg_rsi,
        "ema_rsi": ema_rsi,
        "macd": macd,
        "macd_signal": macd_signal,
        "macd_diff": macd_diff,
        "ema_macd": ema_macd,
        "ema_macd_signal": ema_macd_signal,
        "rsi_divergence": rsi_divergence,
        "flag": flag,
        "macd_trend": macd_trend,
        "bollinger_status": bollinger_status,
        "ema_trend": ema_trend,
        "turnover_status": turnover_status,
        "signal_strength": signal_strength,
        "prev_avg_rsi": prev_avg_rsi,
        "delta_rsi": delta_rsi
    }

    history.append(new_entry)
    save_history(symbol, history)

    print(f"""
✅ FINAL ANALYSIS for {symbol} @ {timestamp}
- price: {price} ({price_trend})
- volume: {volume} ({volume_class})
- 24h change: {change_24h}% ({change_class})
- avg_rsi: {avg_rsi}, ema_rsi: {ema_rsi}
- macd_diff: {macd_diff}, trend: {macd_trend}
- bollinger: {bollinger_status}, ema_trend: {ema_trend}
- turnover check: {turnover_status}
- RSI divergence: {rsi_divergence}, flag: {flag}
- 🔥 signal_strength: {signal_strength}
""")
