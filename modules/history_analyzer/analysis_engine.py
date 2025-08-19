# modules/history_analyzer/analysis_engine.py
# version 2.0, aug 2025

from typing import List, Dict
from utils.get_timestamp import get_timestamp

def analysis_engine(symbol, history_config, collection_entry, analysis_entry):

    print(f"Analysis engine starting...")

    timestamp = get_timestamp()

    print(f"timestamp: {timestamp}")
    print(f"symbol: {symbol}")
    print(f"history_config: {history_config}")
    print(f"collection_entry: {collection_entry}")
    print(f"analysis_entry: {analysis_entry}")

# --- Apufunktiot ---
def analyze_bollinger(price, bb_upper, bb_lower):
    if price is None or bb_upper is None or bb_lower is None:
        return "unknown"
    if price >= bb_upper:
        return "overbought"
    elif price <= bb_lower:
        return "oversold"
    return "neutral"

def detect_ema_trend(price, ema_1d):
    if price is None or ema_1d is None:
        return "unknown"
    if price > ema_1d * 1.01:
        return "strong_above"
    elif price < ema_1d * 0.99:
        return "strong_below"
    return "near_ema"

def detect_turnover_anomaly(turnover, volume, price):
    if turnover is None or volume is None or price is None:
        return "invalid"
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

def detect_macd_trend(macd_diff, threshold=0.01):
    if macd_diff is None or abs(macd_diff) < threshold:
        return "neutral"
    return "bullish" if macd_diff > 0 else "bearish"

def detect_rsi_divergence(history: List[Dict], current_avg: float) -> str:
    if len(history) < CONFIG["rsi_divergence_window"]:
        return "none"

    prev = history[-1]
    prev2 = history[-2]

    if prev["avg_rsi"] is None or prev2["avg_rsi"] is None or current_avg is None:
        return "none"

    if prev["avg_rsi"] > prev2["avg_rsi"] and current_avg < prev["avg_rsi"]:
        return "bearish-divergence"
    elif prev["avg_rsi"] < prev2["avg_rsi"] and current_avg > prev["avg_rsi"]:
        return "bullish-divergence"

    return "none"
