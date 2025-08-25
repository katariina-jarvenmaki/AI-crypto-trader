# modules/history_analyzer/analysis_engine.py
# version 2.0, aug 2025

from typing import List, Dict
from utils.get_timestamp import get_timestamp

def analyze_log_data(symbol, latest, previous, thresholds):

    print(f"🔍 Analyzing symbol: {symbol}")
    print(f"⏱  Time: {latest['timestamp']}  vs.  {previous['timestamp']}")
    timestamp = get_timestamp()
    fetched = latest["fetched"]

    # --- Helpers ---
    def calc_change_and_percent(current, prev):
        if current is None or prev is None:
            return None, None
        try:
            current = float(current)
            prev = float(prev)
            delta = current - prev
            percent = (delta / prev) * 100 if prev != 0 else None
            return delta, percent
        except Exception as e:
            print(f"⚠️ Cannot calculate change: {e}")
            return None, None

    def safe_avg(values):
        clean_values = [v for v in values if v is not None]
        return sum(clean_values) / len(clean_values) if clean_values else None

    def to_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    # Price Data
    price_raw = fetched["price"]
    prev_price_raw = previous["price"]
    price = to_float(price_raw)
    prev_price = to_float(prev_price_raw)
    price_change, price_change_percent = calc_change_and_percent(price, prev_price)

    # RSI Data
    avg_rsi = safe_avg(latest["rsi"].values())
    prev_rsi = previous.get("avg_rsi")
    rsi_change, rsi_change_percent = calc_change_and_percent(avg_rsi, prev_rsi) if avg_rsi is not None and prev_rsi is not None else (None, None)

    # EMA Data
    avg_ema = safe_avg(latest["ema"].values())
    prev_avg_ema = previous.get("avg_ema")
    ema_change, ema_change_percent = calc_change_and_percent(avg_ema, prev_avg_ema) if avg_ema is not None and prev_avg_ema is not None else (None, None)

    # MACD Data
    avg_macd = safe_avg(latest["macd"].values())
    prev_macd = previous.get("avg_macd")
    macd_change, macd_change_percent = calc_change_and_percent(avg_macd, prev_macd) if avg_macd is not None and prev_macd is not None else (None, None)

    # Bollinger Status
    bollinger_mode = thresholds["bollinger_mode"]
    bb_upper_float = to_float(latest["bb_upper"]["1d"])
    bb_lower_float = to_float(latest["bb_lower"]["1d"])
    bollinger_status = analyze_bollinger(price, bb_upper_float, bb_lower_float, bollinger_mode)

    # Trends
    ema_trend_percent = thresholds["ema_trend_percent"]
    ema_1d_float = to_float(latest["ema"]["1d"])
    macd_1d_float = to_float(latest["macd"]["1d"])
    ema_trend = detect_ema_trend(price, ema_1d_float, ema_trend_percent)
    macd_trend = detect_macd_trend(price, macd_1d_float)

    # Flag
    rsi_flag_delta = thresholds["rsi_flag_delta"]
    flag = detect_flag(avg_rsi, prev_rsi, rsi_flag_delta)

    # Signal strength
    signal_strength_rules = thresholds["signal_strength_rules"]
    signal_strength = estimate_signal_strength(
        flag,
        macd_trend,
        bollinger_status,
        ema_trend,
        signal_strength_rules
    )

    # Turnover status
    turnover_deviation = thresholds["turnover_deviation"]
    turnover_float = to_float(fetched["turnover"])
    volume_float = to_float(fetched["volume"])
    turnover_status = detect_turnover_anomaly(turnover_float, volume_float, price, turnover_deviation)

    # RSI Divergence
    history = [{"avg_rsi": prev_rsi},{"avg_rsi": avg_rsi}]
    rsi_divergence = detect_rsi_divergence(history, avg_rsi)

    print(f"✅ Analysis complete")

    return {
        "symbol": symbol,
        "timestamp": timestamp,

        # Price
        "price": str(price_raw),
        "price_change": str(price_change) if price_change is not None else None,
        "price_change_percent": str(price_change_percent) if price_change_percent is not None else None,

        # RSI (avg)
        "avg_rsi": str(avg_rsi) if avg_rsi is not None else None,
        "rsi_change": str(rsi_change) if rsi_change is not None else None,
        "rsi_change_percent": str(rsi_change_percent) if rsi_change_percent is not None else None,

        # EMA
        "avg_ema": str(avg_ema) if avg_ema is not None else None,
        "ema_change": str(ema_change) if ema_change is not None else None,
        "ema_change_percent": str(ema_change_percent) if ema_change_percent is not None else None,

        # MACD
        "avg_macd": str(avg_macd) if avg_macd is not None else None,
        "macd_change": str(macd_change) if macd_change is not None else None,
        "macd_change_percent": str(macd_change_percent) if macd_change_percent is not None else None,

        # Trends and statuses (nämä voi jäädä normaaliksi, koska eivät ole tarkkoja lukuja)
        "ema_trend": ema_trend,
        "macd_trend": macd_trend,
        "bollinger_status": bollinger_status,
        "signal_strength": signal_strength,
        "flag": flag,

        # Analyses
        "turnover_status": turnover_status,
        "rsi_divergence": rsi_divergence
    }

def analyze_latest_only(symbol, latest: dict, thresholds) -> dict:
    """
    Analyzes only symbol data for last entry (without previous-data).
    Returns same structure as analyze_log_data, but missing the fields are = None.
    """
    print(f"\n🔍 Analyzing (only latest): {symbol}")

    def to_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    price_raw = latest["fetched"]["price"]
    price = to_float(price_raw)

    avg_rsi = sum(v for v in latest["rsi"].values() if v is not None) / max(
        1, len([v for v in latest["rsi"].values() if v is not None])
    )
    avg_ema = sum(v for v in latest["ema"].values() if v is not None) / max(
        1, len([v for v in latest["ema"].values() if v is not None])
    )

    macd_pairs = [
        (latest["macd"].get(k), latest["macd_signal"].get(k))
        for k in latest["macd"]
    ]
    macd_diffs = [
        macd - signal for macd, signal in macd_pairs if macd is not None and signal is not None
    ]
    avg_macd = sum(macd_diffs) / len(macd_diffs) if macd_diffs else None

    bollinger_mode = thresholds["bollinger_mode"]
    bollinger_status = analyze_bollinger(price, latest["bb_upper"]["1d"], latest["bb_lower"]["1d"], bollinger_mode)
    ema_trend_percent = thresholds["ema_trend_percent"]
    ema_trend = detect_ema_trend(price, latest["ema"]["1d"], ema_trend_percent)
    macd_trend = detect_macd_trend(price, latest["macd"]["1d"])

    print(f"✅ Analysis complete")

    return {
        "symbol": symbol,
        "timestamp": latest["timestamp"],

        "price": str(price_raw),
        "price_change": None,
        "price_change_percent": None,

        "avg_rsi": str(avg_rsi) if avg_rsi is not None else None,
        "rsi_change": None,
        "rsi_change_percent": None,

        "avg_ema": str(avg_ema) if avg_ema is not None else None,
        "ema_change": None,
        "ema_change_percent": None,

        "avg_macd": str(avg_macd) if avg_macd is not None else None,
        "macd_change": None,
        "macd_change_percent": None,

        "ema_trend": ema_trend,
        "macd_trend": macd_trend,
        "bollinger_status": bollinger_status,
        "signal_strength": None,
        "flag": None,

        "turnover_status": None,
        "rsi_divergence": None,
    }

def analyze_bollinger(price, bb_upper, bb_lower, mode="strict"):
    if price is None or bb_upper is None or bb_lower is None:
        return "unknown"
    if mode == "strict":
        if price >= bb_upper:
            return "overbought"
        elif price <= bb_lower:
            return "oversold"
    return "neutral"

def detect_ema_trend(price, ema_1d, threshold=0.01):
    if price is None or ema_1d is None:
        return "unknown"
    if price > ema_1d * (1 + threshold):
        return "strong_above"
    elif price < ema_1d * (1 - threshold):
        return "strong_below"
    return "near_ema"

def detect_turnover_anomaly(turnover, volume, price, deviation_threshold=0.02):
    if turnover is None or volume is None or price is None:
        return "invalid"
    if volume == 0:
        return "invalid"
    avg_price = turnover / volume
    deviation = abs(avg_price - price) / price
    return "mismatch" if deviation > deviation_threshold else "normal"

def detect_flag(curr_rsi, prev_rsi, delta=5):
    try:
        curr_rsi = float(curr_rsi) if curr_rsi is not None else None
        prev_rsi = float(prev_rsi) if prev_rsi is not None else None
    except (TypeError, ValueError):
        return "neutral"
    if prev_rsi is None or curr_rsi is None:
        return "neutral"
    if curr_rsi > prev_rsi + delta:
        return "bullish"
    elif curr_rsi < prev_rsi - delta:
        return "bearish"
    return "neutral"

def estimate_signal_strength(flag, macd_trend, bollinger_status, ema_trend, rules=None):
    if rules is None:
        rules = {
            "very_strong_bullish": ["bullish", "bullish", "oversold", "strong_above"],
            "very_strong_bearish": ["bearish", "bearish", "overbought", "strong_below"],
        }
    for label, conditions in rules.items():
        if [flag, macd_trend, bollinger_status, ema_trend] == conditions:
            return label
    if flag != "neutral":
        return "watch_for_reversal"
    return "neutral"

def detect_macd_trend(price, macd_value):
    if price is None or macd_value is None:
        return "neutral"
    if price > macd_value:
        return "up"
    elif price < macd_value:
        return "down"
    else:
        return "neutral"

def detect_rsi_divergence(history: List[Dict], current_avg: float) -> str:
    if len(history) < 2:
        return "none"

    prev = history[-1]
    prev2 = history[-2]

    try:
        prev_val = float(prev.get("avg_rsi")) if prev.get("avg_rsi") is not None else None
        prev2_val = float(prev2.get("avg_rsi")) if prev2.get("avg_rsi") is not None else None
        curr_val = float(current_avg) if current_avg is not None else None
    except (TypeError, ValueError):
        return "none"

    if prev_val is None or prev2_val is None or curr_val is None:
        return "none"

    if prev_val > prev2_val and curr_val < prev_val:
        return "bearish-divergence"
    elif prev_val < prev2_val and curr_val > prev_val:
        return "bullish-divergence"

    return "none"

def analysis_engine(symbol: str, history_config: Dict, collection_entry: Dict, analysis_entry: Dict):

    config = history_config.get("history_analyzer")
    thresholds = config.get("analysis_thresholds", {})

    latest = collection_entry
    previous = analysis_entry if analysis_entry else None

    if previous:
        return analyze_log_data(
            symbol, latest, previous, thresholds
        )
    else:
        return analyze_latest_only(
            symbol, latest, thresholds
        )