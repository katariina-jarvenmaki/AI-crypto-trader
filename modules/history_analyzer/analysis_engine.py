# modules/history_analyzer/analysis_engine.py

import json
from typing import List, Dict
from collections import defaultdict
from datetime import datetime, timedelta
from modules.history_analyzer.config_history_analyzer import CONFIG
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from modules.history_analyzer.utils import format_value, decimals_in_number, format_change_for_price_data, format_change

def analyze_log_data(symbol, latest, previous):

    print(f"\n🔍 Analysoidaan symbolia: {symbol}")
    print(f"⏱ Aika: {latest['timestamp']}  vs.  {previous['timestamp']}")

    # --- Lasketaan puuttuvat analyysit, jos eivät ole mukana ---
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

    # --- Tulostukset ---
    print(format_change_for_price_data(latest.get("price"), previous.get("price"), "Hinta"))
    print(format_change(latest.get("avg_rsi_all"), previous.get("avg_rsi_all"), "RSI (avg)"))
    print(format_change(latest.get("ema_rsi"), previous.get("ema_rsi"), "EMA RSI"))
    print(format_change(latest.get("macd_diff"), previous.get("macd_diff"), "MACD ero"))

    print("\n📈 Trendianalyysit:")
    print(f"MACD trendi: {previous.get('macd_trend')} ➜ {latest.get('macd_trend')}")
    print(f"Bollinger status: {previous.get('bollinger_status')} ➜ {latest.get('bollinger_status')}")
    print(f"EMA trendi: {previous.get('ema_trend')} ➜ {latest.get('ema_trend')}")
    print(f"Signaalin vahvuus: {previous.get('signal_strength')} ➜ {latest.get('signal_strength')}")

    # Turnover-analyysi
    print("\n💱 Turnover-analyysi:")
    turnover_status = detect_turnover_anomaly(latest["turnover"], latest["volume"], latest["price"])
    print(f"Turnover vs. hinta: {turnover_status}")

    # 🔍 RSI-divergenssianalyysi
    print("\n🔎 RSI Divergenssianalyysi:")
    history = [
        {"avg_rsi": previous.get("avg_rsi_all")},
        {"avg_rsi": latest.get("avg_rsi_all")},
    ]
    avg_rsi = latest.get("avg_rsi_all")
    prev_avg = previous.get("avg_rsi_all")

    divergence = detect_rsi_divergence(history, avg_rsi)
    delta = abs(avg_rsi - prev_avg) if prev_avg is not None else None

    print(f"Divergenssi: {divergence}")
    if delta is not None:
        print(f"RSI muutos: {delta:.2f} (kynnys: {CONFIG['rsi_change_threshold']})")
        if delta < CONFIG["rsi_change_threshold"]:
            print("⚠️  RSI-muutos alle kynnyksen — divergenssi ei luotettava.")
        else:
            if divergence != "none":
                print(f"🚨 RSI Divergenssi havaittu: {divergence.upper()}")

    # Tarkastellaan käänteitä tai trendejä
    print("\n⚠️  Muutokset tai poikkeamat:")
    if latest.get("flag") != previous.get("flag"):
        print(f"🔁 RSI-lippu muuttunut: {previous.get('flag')} ➜ {latest.get('flag')}")
    if latest.get("signal_strength") != previous.get("signal_strength"):
        print(f"🔥 Signaalivahvuus muuttunut: {previous.get('signal_strength')} ➜ {latest.get('signal_strength')}")

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

    for symbol in symbols:
        entry_pair = history_data.get(symbol)
        if not entry_pair:
            print(f"[{symbol}] Ei löydetty riittävästi vertailukelpoista dataa.")
            continue
        analyze_log_data(symbol, entry_pair["latest"], entry_pair["previous"])
