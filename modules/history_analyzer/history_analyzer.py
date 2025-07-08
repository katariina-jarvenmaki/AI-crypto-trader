# modules/history_analyzer/history_analyzer.py

import os
import sys
import json
import math
from pathlib import Path
from typing import Dict, List

from modules.history_analyzer.config_history_analyzer import CONFIG

print(f"symbol_log_path: {CONFIG['symbol_log_path']}")
print(f"ohlcv_log_path: {CONFIG['ohlcv_log_path']}")
print(f"intervals_to_use: {CONFIG['intervals_to_use']}")
print(f"rsi_change_threshold: {CONFIG['rsi_change_threshold']}")
print(f"ema_alpha: {CONFIG['ema_alpha']}")
print(f"macd_diff_threshold: {CONFIG['macd_diff_threshold']}")
print(f"rsi_divergence_window: {CONFIG['rsi_divergence_window']}")
print(f"symbol_keys: {CONFIG['symbol_keys']}")

def compute_ema_rsi(prev_ema: float, current_avg: float, alpha: float = None) -> float:
    if alpha is None:
        alpha = CONFIG["ema_alpha"]
    if prev_ema is None:
        return current_avg
    return alpha * current_avg + (1 - alpha) * prev_ema

def compute_macd_diff(macd: Dict[str, float], signal: Dict[str, float]) -> float:
    diffs = []
    for interval in CONFIG["intervals_to_use"]:
        m = macd.get(interval)
        s = signal.get(interval)
        if isinstance(m, (float, int)) and isinstance(s, (float, int)):
            diffs.append(m - s)
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

def detect_flag(prev_avg: float, current_avg: float) -> str:
    if current_avg > prev_avg:
        return "bull-flag"
    elif current_avg < prev_avg:
        return "bear-flag"
    return "neutral"

def save_history(symbol: str, data: List[Dict]):
    filepath = os.path.join(CONFIG["history_log_path"])
    all_data = {}
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            all_data = json.load(f)
    all_data[symbol] = data
    with open(filepath, "w") as f:
        json.dump(all_data, f, indent=2)

def debug_print_rsi_data(rsi_data):
    print("  🔍 RSI data:")
    for k, v in rsi_data.items():
        print(f"   - {k}: {v} (type: {type(v)})")

def process_log_entry(entry: dict):
    parsed = parse_log_entry(entry)
    symbol = parsed["symbol"]
    timestamp = parsed["timestamp"]
    current_rsi = parsed["rsi"]
    macd = parsed["macd"]
    macd_signal = parsed["macd_signal"]
    print(f"symbol: {symbol}")
    print(f"timestamp: {timestamp}")
    print(f"current_rsi: {current_rsi}")
    print(f"macd: {macd}")
    print(f"macd_signal: {macd_signal}")    

    print(f"\n🔍 Processing symbol: {symbol} @ {timestamp}")
    # debug_print_rsi_data(current_rsi)

    avg_rsi = average_rsi(current_rsi)
    if avg_rsi is None:
        print(f"❌ Skipping {symbol}: no valid RSI values")
        return
 
    history = load_history(symbol)
    last_entry = history[-1] if history else None

    prev_avg = last_entry.get("avg_rsi") if last_entry else None
    prev_ema_rsi = last_entry.get("ema_rsi") if last_entry else None

    ema_rsi = compute_ema_rsi(prev_ema_rsi, avg_rsi)
    macd_diff = compute_macd_diff(macd, macd_signal)
    divergence = detect_rsi_divergence(history, avg_rsi)
    print(f"prev_avg: {prev_avg}")
    print(f"ema_rsi: {ema_rsi}")
    print(f"prev_ema_rsi: {prev_ema_rsi}")
    print(f"macd_diff: {macd_diff}")
    print(f"divergence: {avg_rsi}")

    delta = abs(avg_rsi - prev_avg) if prev_avg is not None else None
    if delta is not None:
        print(f"➡️  Δ avg_rsi: {delta:.4f} vs threshold: {CONFIG['rsi_change_threshold']}")
        if delta < CONFIG["rsi_change_threshold"]:
            print(f"⚠️  Skipping {symbol}: Δ avg_rsi too small ({delta:.4f})")
            return

    flag = detect_flag(prev_avg, avg_rsi) if prev_avg is not None else "neutral"

    if macd_diff is not None and abs(macd_diff) > CONFIG["macd_diff_threshold"]:
        macd_trend = "bull" if macd_diff > 0 else "bear"
    else:
        macd_trend = "unknown"

    new_entry = {
        "timestamp": timestamp,
        "rsi": current_rsi,
        "avg_rsi": avg_rsi,
        "ema_rsi": ema_rsi,
        "macd_diff": macd_diff,
        "rsi_divergence": divergence,
        "flag": flag,
        "macd_signal": macd_trend,
    }

    print(f"""
✅ FINAL ANALYSIS for {symbol}:
 - avg_rsi: {avg_rsi}
 - prev_avg: {prev_avg}
 - ema_rsi: {ema_rsi}
 - macd_diff: {macd_diff}
 - rsi_divergence: {divergence}
 - flag: {flag}
 - macd_trend: {macd_trend}
""")

    history.append(new_entry)
    save_history(symbol, history)
    print(f"💾 Saved history for {symbol} ({len(history)} total entries)")

def load_history(symbol: str) -> List[Dict]:
    filepath = os.path.join(CONFIG["history_log_path"])
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            all_data = json.load(f)
            return all_data.get(symbol, [])
    return []

def average_rsi(rsi_data: Dict[str, float]) -> float:
    valid_rsi = []
    for v in rsi_data.values():
        try:
            if isinstance(v, (float, int)) and not math.isnan(v):
                valid_rsi.append(v)
        except:
            continue
    if not valid_rsi:
        print(f"⚠️  All RSI values invalid or NaN: {rsi_data}")
    return sum(valid_rsi) / len(valid_rsi) if valid_rsi else None

def parse_log_entry(entry: dict) -> Dict:
    symbol = entry["symbol"]
    timestamp = entry["timestamp"]
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
        "rsi": rsi_data,
        "macd": macd_data,
        "macd_signal": signal_data
    }

def process_latest_entries_for_symbols(symbols: List[str], ohlcv_log_path: str):

    seen = set()
    with open(ohlcv_log_path, "r") as f:
        for line in reversed(f.readlines()):
            try:
                entry = json.loads(line.strip())
                symbol = entry.get("symbol")
                if symbol in symbols and symbol not in seen:
                    process_log_entry(entry)
                    seen.add(symbol)
                if len(seen) == len(symbols):
                    break
            except Exception as e:
                print(f"Skipping invalid OHLCV line: {e}")

def get_latest_symbols_from_log(file_path: str) -> List[str]:
    with open(file_path, "r") as f:
        lines = f.readlines()
        if not lines:
            return []
        last_entry = json.loads(lines[-1])
        
        combined_symbols = set()  # 🔧 Tämä puuttui
        for key in CONFIG["symbol_keys"]:
            combined_symbols.update(last_entry.get(key, []))

        return list(combined_symbols)

def main():

    symbols = get_latest_symbols_from_log(CONFIG["symbol_log_path"])
    if not symbols:
        print("No symbols found in latest symbol log.")
        return
    print(f"Found {len(symbols)} symbols to process...")
    process_latest_entries_for_symbols(symbols, CONFIG["ohlcv_log_path"])

if __name__ == "__main__":
    main()
