# modules/history_analyzer/history_analyzer.py

import os
import json
import math
from typing import Dict, List
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
    filepath = os.path.join(CONFIG["history_log_path"])
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
    else:
        data = {}

    data[symbol] = history

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

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
    filepath = os.path.join(CONFIG["history_log_path"])
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return []
    symbol_history = data.get(symbol, [])
    if not isinstance(symbol_history, list):
        return []
    return symbol_history

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

def parse_log_entry(entry: dict) -> dict:
    symbol = entry["symbol"]
    timestamp = entry["timestamp"]

    price = entry["data_preview"].get("1m", {}).get("close")
    price_data = entry["data_preview"].get("price_data", {})
    volume = price_data.get("volume")
    change_24h = price_data.get("price_change_percent")

    # ➕ override with price_data if exists
    price_data = entry["data_preview"].get("price_data", {})
    price = price_data.get("last_price", price)
    volume = price_data.get("volume", volume)
    change_24h = price_data.get("price_change_percent", change_24h)

    rsi_data = {
        interval: entry["data_preview"].get(interval, {}).get("rsi")
        for interval in CONFIG["intervals_to_use"]
    }
    macd_data = {
        interval: entry["data_preview"].get(interval, {}).get("macd")
        for interval in CONFIG["intervals_to_use"]
    }
    signal_data = {
        interval: entry["data_preview"].get(interval, {}).get("macd_signal")
        for interval in CONFIG["intervals_to_use"]
    }

    return {
        "symbol": symbol,
        "timestamp": timestamp,
        "price": price,
        "volume": volume,
        "change_24h": change_24h,
        "rsi": rsi_data,
        "macd": macd_data,
        "macd_signal": signal_data,
    }

def process_latest_entries_for_symbols(symbols: List[str]):
    seen = set()
    price_data_entries = get_latest_price_data_for_symbols(symbols)

    with open(CONFIG["ohlcv_log_path"], "r") as f:
        for line in reversed(f.readlines()):
            try:
                entry = json.loads(line.strip())
                symbol = entry.get("symbol")

                if symbol in symbols and symbol not in seen:
                    price_entry = price_data_entries.get(symbol)
                    if price_entry:
                        entry["data_preview"]["price_data"] = price_entry["data_preview"]
                    process_log_entry(entry) 
                    seen.add(symbol)

                if len(seen) == len(symbols):
                    break
            except Exception as e:
                print(f"Skipping invalid OHLCV line: {e}")

def get_latest_price_data_for_symbols(symbols: List[str]) -> dict:
    """
    Palauttaa dictin muodossa viimeisimmän price data -rivin per symbol.
    """
    latest = {}
    with open(CONFIG["price_log_path"], "r") as f:
        for line in reversed(f.readlines()):
            try:
                entry = json.loads(line.strip())
                symbol = entry.get("symbol")
                if symbol in symbols and symbol not in latest:
                    latest[symbol] = entry
                if len(latest) == len(symbols):
                    break
            except Exception as e:
                print(f"Skipping invalid PRICE line: {e}")
    return latest

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

def get_latest_symbols_from_log(file_path: str) -> List[str]:

    with open(file_path, "r") as f:
        lines = f.readlines()
        if not lines:
            return []
        last_entry = json.loads(lines[-1])

        combined_symbols = set()
        for key in CONFIG["symbol_keys"]:
            combined_symbols.update(last_entry.get(key, []))

        return list(combined_symbols)

def main():

    symbols = get_latest_symbols_from_log(CONFIG["symbol_log_path"])

    if not symbols:
        print("No symbols found in latest symbol log.")
        return
    print(f"Found {len(symbols)} symbols to process...")
    process_latest_entries_for_symbols(symbols)

if __name__ == "__main__":
    main()