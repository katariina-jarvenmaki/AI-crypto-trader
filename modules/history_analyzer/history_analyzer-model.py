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













import json
import os
from datetime import datetime
from typing import Dict, List

# 🔧 KONFIGURAATIO
CONFIG = {
    "intervals_to_use": ["1h", "4h", "1d", "1w"],
    "rsi_change_threshold": 2.0,
    "ema_alpha": 0.2,
    "macd_diff_threshold": 0.5,
    "rsi_divergence_window": 2,
    "data_dir": "rsi_logs",
}

def parse_log_entry(entry: dict) -> Dict:
    symbol = entry["symbol"]
    timestamp = entry["timestamp"]
    price = entry["data_preview"].get("1m", {}).get("close")
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

def load_history(symbol: str) -> List[Dict]:
    filepath = os.path.join(CONFIG["data_dir"], f"{symbol}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return []

def save_history(symbol: str, data: List[Dict]):
    os.makedirs(CONFIG["data_dir"], exist_ok=True)
    filepath = os.path.join(CONFIG["data_dir"], f"{symbol}.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def average_rsi(rsi_data: Dict[str, float]) -> float:
    valid_rsi = [v for v in rsi_data.values() if isinstance(v, (float, int))]
    return sum(valid_rsi) / len(valid_rsi) if valid_rsi else None

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

def process_log_entry(entry: dict):
    parsed = parse_log_entry(entry)
    symbol = parsed["symbol"]
    timestamp = parsed["timestamp"]
    current_rsi = parsed["rsi"]
    macd = parsed["macd"]
    macd_signal = parsed["macd_signal"]

    avg_rsi = average_rsi(current_rsi)
    if avg_rsi is None:
        return

    history = load_history(symbol)
    last_entry = history[-1] if history else None

    prev_avg = last_entry.get("avg_rsi") if last_entry else None
    prev_ema_rsi = last_entry.get("ema_rsi") if last_entry else None

    ema_rsi = compute_ema_rsi(prev_ema_rsi, avg_rsi)
    macd_diff = compute_macd_diff(macd, macd_signal)
    divergence = detect_rsi_divergence(history, avg_rsi)

    delta = abs(avg_rsi - prev_avg) if prev_avg is not None else None
    if delta is not None and delta < CONFIG["rsi_change_threshold"]:
        return

    flag = detect_flag(prev_avg, avg_rsi) if prev_avg is not None else "neutral"

    # MACD-signalin lisähavainto
    if macd_diff is not None and abs(macd_diff) > CONFIG["macd_diff_threshold"]:
        macd_trend = "bullish" if macd_diff > 0 else "bearish"
    else:
        macd_trend = "neutral"

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

    history.append(new_entry)
    save_history(symbol, history)
    print(f"Processed {symbol}: {flag} ({divergence}, MACD: {macd_trend}) @ {timestamp}")

def process_log_file(file_path: str):
    with open(file_path, "r") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                process_log_entry(entry)
            except Exception as e:
                print(f"Skipping invalid line: {e}")

def get_latest_symbols_from_log(file_path: str) -> List[str]:
    with open(file_path, "r") as f:
        lines = f.readlines()
        if not lines:
            return []
        last_entry = json.loads(lines[-1])
        combined_symbols = (
            last_entry.get("potential_both_ways", []) +
            last_entry.get("potential_to_long", []) +
            last_entry.get("potential_to_short", [])
        )
        return list(set(combined_symbols))  # Poistaa duplikaatit

def process_latest_entries_for_symbols(symbols: List[str], ohlcv_log_path: str):
    seen = set()
    with open(ohlcv_log_path, "r") as f:
        for line in reversed(f.readlines()):  # Käydään tiedosto takaperin
            try:
                entry = json.loads(line.strip())
                symbol = entry.get("symbol")
                if symbol in symbols and symbol not in seen:
                    process_log_entry(entry)
                    seen.add(symbol)
                if len(seen) == len(symbols):
                    break  # Kaikki symbolit käsitelty
            except Exception as e:
                print(f"Skipping invalid OHLCV line: {e}")

def main():
    symbol_log_path = "modules/symbol_data_fetcher/symbol_data_log.jsonl"
    ohlcv_log_path = "integrations/multi_interval_ohlcv/ohlcv_fetch_log.jsonl"
    symbols = get_latest_symbols_from_log(symbol_log_path)
    if not symbols:
        print("No symbols found in latest symbol log.")
        return
    print(f"Found {len(symbols)} symbols to process...")
    process_latest_entries_for_symbols(symbols, ohlcv_log_path)

if __name__ == "__main__":
    main()
