import json
import pprint
from dateutil import parser
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict

from modules.history_analyzer.config_history_analyzer import CONFIG
from modules.symbol_data_fetcher.config_symbol_data_fetcher import LOCAL_TIMEZONE

def parse_log_entry(entry: Dict) -> Dict:
    dt = parser.isoparse(entry["timestamp"])
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    entry["timestamp"] = dt
    return entry

def filter_logs_by_time(logs: List[Dict], since: timedelta) -> List[Dict]:
    now = datetime.now(LOCAL_TIMEZONE)
    return [log for log in logs if now - log["timestamp"] <= since]

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

def compute_bias(logs: List[Dict], time_window_hours: float = 24.0) -> Dict:
    logs = [parse_log_entry(entry) for entry in logs]

    def aggregate_bias(time_delta: timedelta):
        filtered_logs = filter_logs_by_time(logs, time_delta)
        if not filtered_logs:
            return None

        latest_per_symbol = {}
        for log in sorted(filtered_logs, key=lambda x: x["timestamp"], reverse=True):
            if log["symbol"] not in latest_per_symbol:
                latest_per_symbol[log["symbol"]] = log

        scores = [score_entry(entry) for entry in latest_per_symbol.values()]
        avg_score = sum(scores) / len(scores)
        bias = max(-1.0, min(1.0, avg_score / 3.0))  # Normalize
        return {
            "avg_score": avg_score,
            "count": len(latest_per_symbol),
            "bias": bias,
        }

    # Päätaso: 24h
    daily = aggregate_bias(timedelta(hours=time_window_hours))
    if not daily:
        return {"broad_state": "neutral", "broad_bias": 0.0}

    broad_state = determine_market_state(daily["avg_score"])
    result = {
        "broad_state": broad_state,
        "broad_bias": round(daily["bias"], 3),
        "avg_score": round(daily["avg_score"], 3),
        "coins_counted": daily["count"]
    }

    recent = aggregate_bias(timedelta(hours=1.0))

    if recent:
        recent_state = determine_market_state(recent["avg_score"])
        result["last_hour_state"] = recent_state
        result["last_hour_bias"] = round(recent["bias"], 3)

        if broad_state != recent_state and abs(recent["bias"] - daily["bias"]) > 0.5:
            result["warning"] = f"Market trend reversal detected (24h: {broad_state}, 1h: {recent_state})"
            result["adjusted_bias"] = round((daily["bias"] + recent["bias"]) / 2.0, 3)

    return result

if __name__ == "__main__":
    with open(CONFIG["analysis_log_path"], "r") as f:
        data = [json.loads(line) for line in f]

    result = compute_bias(data, time_window_hours=24.0)
    pprint.pprint(result)

