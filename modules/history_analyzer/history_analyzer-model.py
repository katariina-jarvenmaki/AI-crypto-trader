import json
import os
import math
from typing import Dict, List
import matplotlib.pyplot as plt
from datetime import datetime

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
    volume = entry["data_preview"].get("1d", {}).get("volume")
    change_24h = entry["data_preview"].get("1d", {}).get("change_24h")

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

def average_rsi(rsi_data: Dict[str, float]) -> float:
    valid_rsi = [v for v in rsi_data.values() if isinstance(v, (float, int)) and not math.isnan(v)]
    return sum(valid_rsi) / len(valid_rsi) if valid_rsi else None

def compute_ema_rsi(prev_ema: float, current_avg: float, alpha: float = None) -> float:
    if alpha is None:
        alpha = CONFIG["ema_alpha"]
    if prev_ema is None:
        return current_avg
    return alpha * current_avg + (1 - alpha) * prev_ema

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

    avg_rsi = average_rsi(current_rsi)
    if avg_rsi is None:
        return

    history = load_history(symbol)
    last_entry = history[-1] if history else None

    prev_avg = last_entry.get("avg_rsi") if last_entry else None
    prev_ema_rsi = last_entry.get("ema_rsi") if last_entry else None
    prev_price = last_entry.get("price") if last_entry else None

    ema_rsi = compute_ema_rsi(prev_ema_rsi, avg_rsi)
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

    # 📊 Uudet analyysit:
    price_trend = detect_price_trend(prev_price, price)
    volume_class = classify_volume(volume)
    change_class = interpret_change_24h(change_24h)

    new_entry = {
        "timestamp": timestamp,
        "rsi": current_rsi,
        "avg_rsi": avg_rsi,
        "ema_rsi": ema_rsi,
        "macd_diff": macd_diff,
        "rsi_divergence": divergence,
        "flag": flag,
        "macd_signal": macd_trend,
        "price": price,
        "price_trend": price_trend,
        "volume": volume,
        "volume_class": volume_class,
        "change_24h": change_24h,
        "change_class": change_class,
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
- macd_diff: {macd_diff}
- rsi_divergence: {divergence}
- flag: {flag}
- macd_trend: {macd_trend}
""")

# 📊 UUSI: Market-tilan päättely

# patch_history_with_market_state("BTCUSDT")
# plot_market_history("BTCUSDT")
# print(get_last_strong_market_state("BTCUSDT"))

def determine_market_state(entry):
    if (
        entry["macd_signal"] == "bullish"
        and entry["flag"] == "bull-flag"
        and entry["change_class"] in ["strong-up", "mild-up"]
        and entry["volume_class"] in ["medium-volume", "high-volume"]
    ):
        return "bull"
    elif (
        entry["macd_signal"] == "bearish"
        and entry["flag"] == "bear-flag"
        and entry["change_class"] in ["strong-down", "mild-down"]
        and entry["volume_class"] in ["medium-volume", "high-volume"]
    ):
        return "bear"
    else:
        return "neutral"

# ✅ Päivitää history-tiedostoon market_state

def patch_history_with_market_state(symbol):
    history = load_history(symbol)
    for entry in history:
        entry["market_state"] = determine_market_state(entry)
    save_history(symbol, history)

# 📈 Visualisointi

def plot_market_history(symbol):
    history = load_history(symbol)
    if not history:
        print(f"Ei dataa symbolille: {symbol}")
        return

    dates = [datetime.fromisoformat(e["timestamp"]) for e in history]
    ema_rsi = [e.get("ema_rsi") for e in history]
    market_state = [e.get("market_state", "neutral") for e in history]

    color_map = {"bull": "green", "bear": "red", "neutral": "gray"}
    state_colors = [color_map.get(state, "gray") for state in market_state]

    plt.figure(figsize=(14, 6))
    plt.title(f"EMA-RSI ja market_state: {symbol}")
    plt.xlabel("Aika")
    plt.ylabel("EMA-RSI")

    plt.plot(dates, ema_rsi, label="EMA-RSI", color="blue")
    plt.scatter(dates, ema_rsi, c=state_colors, label="Market State", s=20)
    plt.legend()
    plt.tight_layout()
    plt.grid(True)
    plt.show()

# ✨ Valinnainen: Hae viimeisin ei-neutral

def get_last_strong_market_state(symbol):
    history = load_history(symbol)
    for entry in reversed(history):
        if entry.get("market_state") in ["bull", "bear"]:
            return entry
    return None
