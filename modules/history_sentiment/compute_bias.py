# modules/history_sentiment/compute_bias.py
# version 2.0, aug 2025

from dateutil import parser
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from utils.get_timestamp import get_timestamp

def parse_log_entry(entry: Dict) -> Dict:

    ts = entry["timestamp"]
    if isinstance(ts, str):
        dt = parser.isoparse(ts)
    else:
        dt = ts

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    entry["timestamp"] = dt
    return entry

def filter_values_by_time(values: List[Dict], since: timedelta) -> List[Dict]:
    now = parser.isoparse(get_timestamp())
    cutoff = now - since
    filtered = [log for log in values if log["timestamp"] >= cutoff]
    return filtered

def score_entry(entry: Dict) -> float:
    score = 0.0

    # MACD trend
    macd_map = {"bullish": 1, "bearish": -1, "neutral": 0}
    score += macd_map.get(entry.get("macd_trend", "neutral"), 0)

    # EMA trend
    ema_map = {
        "strong_above": 1,
        "weak_above": 0.5,
        "strong_below": -1,
        "weak_below": -0.5,
        "neutral": 0
    }
    score += ema_map.get(entry.get("ema_trend", "neutral"), 0)

    # Bollinger status
    bb_map = {
        "overbought": 0.5,
        "oversold": -0.5,
        "neutral": 0
    }
    score += bb_map.get(entry.get("bollinger_status", "neutral"), 0)

    # Optional: RSI over 70/30 bias
    rsi_1d = entry.get("rsi", {}).get("1d", None)
    if rsi_1d:
        if rsi_1d > 70:
            score += 0.5
        elif rsi_1d < 30:
            score -= 0.5

    return score

def determine_market_state(avg_score: float, threshold: float = 0.5) -> str:
    if avg_score > threshold:
        return "bull"
    elif avg_score < -threshold:
        return "bear"
    else:
        return "neutral"

def compute_bias(values: Dict[str, Dict], time_window_hours: float = 24.0) -> Dict:
    if isinstance(values, dict):
        values = list(values.values())

    values = [parse_log_entry(entry) for entry in values]

    def aggregate_bias(time_delta: timedelta):
        filtered_values = filter_values_by_time(values, time_delta)
        if not filtered_values:
            return None

        symbol_scores = {}
        symbol_movements = {}
        total_entries = len(filtered_values)
        
        for log in filtered_values:
            symbol = log["symbol"]
            score = score_entry(log)
            symbol_scores.setdefault(symbol, []).append(score)

        avg_scores_per_symbol = {s: sum(scores)/len(scores) for s, scores in symbol_scores.items()}
        all_avg_score = sum(avg_scores_per_symbol.values()) / len(avg_scores_per_symbol)
        bias = max(-1.0, min(1.0, all_avg_score / 3.0))

        for symbol, scores in symbol_scores.items():
            if len(scores) < 2:
                continue
            deltas = [abs(scores[i] - scores[i-1]) for i in range(1, len(scores))]
            symbol_movements[symbol] = sum(deltas)/len(deltas)
        
        volatility = sum(symbol_movements.values()) / len(symbol_movements) if symbol_movements else 0.0

        return {
            "avg_score": all_avg_score,
            "bias": bias,
            "volatility": volatility,
            "coins_counted": len(avg_scores_per_symbol),
            "entries_counted": total_entries,
        }

    result = {}
    biases = aggregate_bias(timedelta(hours=time_window_hours))
    if biases:
        result["state"] = determine_market_state(biases["avg_score"])
        result["bias"] = round(biases['bias'], 3)
        result["avg_score"] = round(biases['avg_score'], 3)
        result["volatility"] = round(biases['volatility'], 3)
        result["coins_counted"] = biases['coins_counted']
        result["entries_counted"] = biases['entries_counted']

    return result
