# modules/history_sentiment/compute_bias.py
# version 2.0, aug 2025

from dateutil import parser
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
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

def score_entry(entry: Dict, config: Dict) -> float:
    score = 0.0
    weights = config['compute_bias']['weights']

    # MACD trend
    macd_map = weights.get("macd", {})
    score += macd_map.get(entry.get("macd_trend", "neutral"), 0)

    # EMA trend
    ema_map = weights.get("ema", {})
    score += ema_map.get(entry.get("ema_trend", "neutral"), 0)

    # Bollinger status
    bb_map = weights.get("bollinger", {})
    score += bb_map.get(entry.get("bollinger_status", "neutral"), 0)

    # RSI
    rsi_cfg = config['compute_bias']['rsi_rules']
    rsi_val = entry.get("avg_rsi")

    if rsi_val is not None:
        try:
            rsi_val = float(rsi_val)
        except (ValueError, TypeError):
            rsi_val = None

    if rsi_val is not None:
        if rsi_val > rsi_cfg.get("overbought_threshold", 70):
            score += rsi_cfg.get("weight_overbought", 0.5)
        elif rsi_val < rsi_cfg.get("oversold_threshold", 30):
            score += rsi_cfg.get("weight_oversold", -0.5)

    return score

# def determine_market_state(avg_score: float, config: Dict) -> str:
#     threshold = config['compute_bias']['market_state_threshold']
#     if avg_score > threshold:
#         return "bull"
#     elif avg_score < -threshold:
#         return "bear"
#     else:
#         return "neutral"

def compute_bias(values: List[Dict], config: Dict, time_window_hours: float = 24.0) -> Optional[Dict]:

    if isinstance(values, dict):
        values = list(values.values())
    values = [parse_log_entry(entry) for entry in values]

    def aggregate_bias(time_delta: timedelta):
        filtered = filter_values_by_time(values, time_delta)
        if not filtered:
            return None

        symbol_scores, symbol_movements = {}, {}
        for log in filtered:
            symbol = log["symbol"]
            score = score_entry(log, config)
            symbol_scores.setdefault(symbol, []).append(score)

        avg_scores = {s: sum(v) / len(v) for s, v in symbol_scores.items()}
        all_avg = sum(avg_scores.values()) / len(avg_scores)

        divisor = config['compute_bias']['bias_normalization_divisor']
        bias = max(-1.0, min(1.0, all_avg / divisor))

        for symbol, scores in symbol_scores.items():
            if len(scores) < 2:
                continue
            deltas = [abs(scores[i] - scores[i - 1]) for i in range(1, len(scores))]
            symbol_movements[symbol] = sum(deltas) / len(deltas)

        volume = sum(symbol_movements.values()) / len(symbol_movements) if symbol_movements else 0.0

        return {
            "avg_score": all_avg,
            "bias": bias,
            "volume": volume,
            "coins_counted": len(avg_scores),
            "entries_counted": len(filtered),
        }

    biases = aggregate_bias(timedelta(hours=time_window_hours))
    if not biases:
        return None

#     print(f"biases: {biases}")
#     print(f"state: {determine_market_state(biases['avg_score'], config)}")
#     print(f"bias: {round(biases['bias'], 3)}")
#     print(f"avg_score: {round(biases['avg_score'], 3)}")
#     print(f"volume: {round(biases['volume'], 3)}")
#     print(f"coins_counted: {biases['coins_counted']}")
#     print(f"entries_counted: {biases['entries_counted']}")

#     return {
#         "state": determine_market_state(biases["avg_score"], config),
#         "bias": round(biases["bias"], 3),
#         "avg_score": round(biases["avg_score"], 3),
#         "volume": round(biases["volume"], 3),
#         "coins_counted": biases["coins_counted"],
#         "entries_counted": biases["entries_counted"],
#     }
