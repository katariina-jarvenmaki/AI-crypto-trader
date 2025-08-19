# modules/history_analyzer/analysis_engine.py
# version 2.0, aug 2025

from typing import List, Dict
from utils.get_timestamp import get_timestamp

def analyze_log_data(symbol, latest, previous):
    print(f"\n🔍 Analysoidaan symbolia: {symbol}")

def analyze_latest_only(symbol, latest: dict) -> dict:
    """
    Analysoi symbolin tiedot vain viimeisimmän entryn perusteella (ilman previous-dataa).
    Palauttaa saman rakenteen kuin analyze_log_data, mutta vertailukentät = None.
    """
    print(f"\n🔍 Analysoidaan symbolia (vain latest): {symbol}")

    price = float(latest["fetched"]["price"])
    avg_rsi = sum(v for v in latest["rsi"].values() if v is not None) / max(
        1, len([v for v in latest["rsi"].values() if v is not None])
    )
    ema_rsi = sum(v for v in latest["ema"].values() if v is not None) / max(
        1, len([v for v in latest["ema"].values() if v is not None])
    )

    macd_pairs = [
        (latest["macd"].get(k), latest["macd_signal"].get(k))
        for k in latest["macd"]
    ]
    valid_diffs = [
        macd - signal for macd, signal in macd_pairs if macd is not None and signal is not None
    ]
    macd_diff = sum(valid_diffs) / len(valid_diffs) if valid_diffs else None

    bollinger_status = analyze_bollinger(price, latest["bb_upper"]["1d"], latest["bb_lower"]["1d"])
    ema_trend = detect_ema_trend(price, latest["ema"]["1d"])
    macd_trend = detect_macd_trend(macd_diff)

    return {
        "symbol": symbol,
        "timestamp": latest["timestamp"],

        # Price
        "price": price,
        "price_change": None,
        "price_change_percent": None,

        # RSI
        "avg_rsi_all": avg_rsi,
        "rsi_change": None,
        "rsi_change_percent": None,
        "rsi_delta": None,

        # EMA RSI
        "ema_rsi": ema_rsi,
        "ema_rsi_change": None,
        "ema_rsi_change_percent": None,

        # MACD
        "macd_diff": macd_diff,
        "macd_diff_change": None,
        "macd_diff_change_percent": None,

        # Trends and statuses
        "macd_trend": macd_trend,
        "bollinger_status": bollinger_status,
        "ema_trend": ema_trend,
        "signal_strength": None,
        "flag": None,

        # Analyses
        "turnover_status": None,
        "rsi_divergence": None,
    }

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

def analysis_engine(symbol: str, history_config: Dict, collection_entry: Dict, analysis_entry: Dict):

    print("Analysis engine starting...")

    timestamp = get_timestamp()
    latest = collection_entry
    previous = analysis_entry if analysis_entry else None

    if previous:
        return analyze_log_data(symbol, latest, previous)
    else:
        return analyze_latest_only(symbol, latest)
