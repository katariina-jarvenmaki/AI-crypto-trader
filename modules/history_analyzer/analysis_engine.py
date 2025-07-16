# modules/history_analyzer/analysis_engine.py

import json
from typing import List, Dict
from collections import defaultdict
from datetime import datetime, timedelta
from modules.history_analyzer.config_history_analyzer import CONFIG
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from modules.history_analyzer.utils import format_value, decimals_in_number

def analyze_log_data(symbol, latest, previous):
    print(f"\n🔍 Analysoidaan symbolia: {symbol}")
    print(f"⏱ Aika: {latest['timestamp']}  vs.  {previous['timestamp']}")

    # --- Lasketaan puuttuvat analyysit ---
    for entry, ref in [(latest, previous)]:
        if "bollinger_status" not in entry:
            entry["bollinger_status"] = analyze_bollinger(
                entry["price"],
                entry["bb_upper"]["1d"],
                entry["bb_lower"]["1d"]
            )

        if "ema_trend" not in entry:
            entry["ema_trend"] = detect_ema_trend(entry["price"], entry["ema"]["1d"])

        if "macd_trend" not in entry:
            entry["macd_trend"] = detect_macd_trend(entry["macd_diff"])

        if "flag" not in entry:
            entry["flag"] = detect_flag(ref.get("avg_rsi_all"), entry.get("avg_rsi_all"))

        if "signal_strength" not in entry:
            entry["signal_strength"] = estimate_signal_strength(
                entry["flag"],
                entry["macd_trend"],
                entry["bollinger_status"],
                entry["ema_trend"]
            )

    # --- Lasketaan muutokset ja prosentit ---
    def calc_change_and_percent(current, prev):
        if current is None or prev is None:
            return None, None
        delta = current - prev
        percent = (delta / prev) * 100 if prev != 0 else None
        return delta, percent

    price = latest.get("price")
    prev_price = previous.get("price")
    price_delta, price_percent = calc_change_and_percent(price, prev_price)

    rsi = latest.get("avg_rsi_all")
    prev_rsi = previous.get("avg_rsi_all")
    rsi_delta, rsi_percent = calc_change_and_percent(rsi, prev_rsi)

    ema_rsi = latest.get("ema_rsi")
    prev_ema_rsi = previous.get("ema_rsi")
    ema_rsi_delta, ema_rsi_percent = calc_change_and_percent(ema_rsi, prev_ema_rsi)

    macd = latest.get("macd_diff")
    prev_macd = previous.get("macd_diff")
    macd_delta, macd_percent = calc_change_and_percent(macd, prev_macd)

    # --- Turnover-analyysi ---
    turnover_status = detect_turnover_anomaly(latest["turnover"], latest["volume"], latest["price"])

    # --- RSI Divergenssi ---
    history = [
        {"avg_rsi": previous.get("avg_rsi_all")},
        {"avg_rsi": latest.get("avg_rsi_all")},
    ]
    divergence = detect_rsi_divergence(history, rsi)
    rsi_change_delta = abs(rsi - prev_rsi) if rsi is not None and prev_rsi is not None else None

    # --- Palautettavat analysoidut arvot ---
    return {
        "symbol": symbol,
        "timestamp": latest["timestamp"].isoformat(),
        
        # Hinta
        "price": price,
        "price_change": price_delta,
        "price_change_percent": price_percent,

        # RSI (avg)
        "avg_rsi_all": rsi,
        "rsi_change": rsi_delta,
        "rsi_change_percent": rsi_percent,

        # EMA RSI
        "ema_rsi": ema_rsi,
        "ema_rsi_change": ema_rsi_delta,
        "ema_rsi_change_percent": ema_rsi_percent,

        # MACD
        "macd_diff": macd,
        "macd_diff_change": macd_delta,
        "macd_diff_change_percent": macd_percent,

        # Trendit ja tilat
        "macd_trend": latest.get("macd_trend"),
        "bollinger_status": latest.get("bollinger_status"),
        "ema_trend": latest.get("ema_trend"),
        "signal_strength": latest.get("signal_strength"),
        "flag": latest.get("flag"),

        # Muut analyysit
        "turnover_status": turnover_status,
        "rsi_divergence": divergence,
        "rsi_delta": rsi_change_delta,
    }

# --- Analyysifunktiot ---
def analyze_bollinger(price, bb_upper, bb_lower):
    if price >= bb_upper:
        return "overbought"
    elif price <= bb_lower:
        return "oversold"
    return "neutral"

def detect_ema_trend(price, ema_1d):
    if price > ema_1d * 1.01:
        return "strong_above"
    elif price < ema_1d * 0.99:
        return "strong_below"
    return "near_ema"

def detect_turnover_anomaly(turnover, volume, price):
    if volume == 0:
        return "invalid"
    avg_price = turnover / volume
    deviation = abs(avg_price - price) / price
    return "mismatch" if deviation > 0.02 else "normal"

def detect_flag(prev_rsi, curr_rsi):
    if prev_rsi is None:
        return "neutral"
    if curr_rsi > prev_rsi + 5:
        return "bullish"
    elif curr_rsi < prev_rsi - 5:
        return "bearish"
    return "neutral"

def estimate_signal_strength(flag, macd_trend, bollinger_status, ema_trend):
    if flag == "bullish" and macd_trend == "bullish" and bollinger_status == "oversold" and ema_trend == "strong_above":
        return "very_strong_bullish"
    if flag == "bearish" and macd_trend == "bearish" and bollinger_status == "overbought" and ema_trend == "strong_below":
        return "very_strong_bearish"
    if flag != "neutral":
        return "watch_for_reversal"
    return "neutral"

def detect_macd_trend(macd_diff, threshold=0.5):
    if macd_diff is None or abs(macd_diff) < threshold:
        return "neutral"
    return "bullish" if macd_diff > 0 else "bearish"

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

def load_history_entries_with_prev(symbols, path):
    """
    Lataa uusimmat ja niiden vertailukelpoiset (aiemmat) entryt jokaiselle symbolille.
    """
    entries = defaultdict(list)

    with open(path, "r") as file:
        for line in file:
            try:
                entry = json.loads(line)
                symbol = entry.get("symbol")
                if symbol not in symbols:
                    continue
                timestamp = datetime.fromisoformat(entry["timestamp"])
                entry["timestamp"] = timestamp
                entries[symbol].append(entry)
            except Exception as e:
                print(f"Virhe käsiteltäessä riviä: {e}")

    result = {}
    min_delta_minutes = CONFIG.get("min_prev_entry_age_minutes", 60)
    min_delta = timedelta(minutes=min_delta_minutes)

    for symbol in symbols:
        symbol_entries = sorted(entries[symbol], key=lambda e: e["timestamp"], reverse=True)
        if len(symbol_entries) < 2:
            continue

        latest = symbol_entries[0]
        previous = None

        for entry in symbol_entries[1:]:
            delta = latest["timestamp"] - entry["timestamp"]
            if delta >= min_delta:
                previous = entry
                break

        if previous:
            result[symbol] = {
                "latest": latest,
                "previous": previous
            }

    return result

def analysis_engine(symbols):
    print(f"Analysis engine starting...")

    log_path = CONFIG["history_log_path"]
    history_data = load_history_entries_with_prev(symbols, log_path)

    results = []  

    for symbol in symbols:
        entry_pair = history_data.get(symbol)
        if not entry_pair:
            print(f"[{symbol}] Ei löydetty riittävästi vertailukelpoista dataa.")
            continue
        result = analyze_log_data(symbol, entry_pair["latest"], entry_pair["previous"])
        results.append(result)

    return results
