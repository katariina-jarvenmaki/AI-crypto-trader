import os
import json
import pprint
import pandas as pd
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

def log_sentiment_result(result: Dict, trend_event: dict | tuple | None = None) -> None:
    """Tallenna analyysitulos ja mahdollinen trendimuutos lokitiedostoon."""
    log_path = CONFIG["sentiment_log_path"]
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Rakenna lokimerkintä
    result_entry = {
        "timestamp": datetime.now(LOCAL_TIMEZONE).isoformat(),
        "result": result
    }

    if trend_event:
        ts, direction, amount = trend_event
        result_entry["trend_shift"] = {
            "timestamp": ts,
            "direction": direction,
            "change": amount
        }

    # Kirjoita rivinä JSONL-lokiin
    with open(log_path, "a") as f:
        f.write(json.dumps(result_entry) + "\n")

import json
from datetime import datetime
import pandas as pd

def detect_trend_shifts(
    metric: str = "broad_bias",
    window: int = 3,
    threshold: float = 0.02,
    direction: str = "both"  # vaihtoehdot: "down", "up", "both"
):
    file_path = "../AI-crypto-trader-logs/analysis-data/history_sentiment_log.jsonl"

    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))

    df = pd.DataFrame([
        {
            "timestamp": datetime.fromisoformat(item["timestamp"]),
            metric: item["result"][metric]
        }
        for item in data
        if metric in item["result"]
    ])

    df.sort_values("timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)

    last_event = None

    for i in range(len(df) - window):
        start_val = df[metric].iloc[i]
        end_val = df[metric].iloc[i + window]
        change = end_val - start_val

        timestamp = df["timestamp"].iloc[i].isoformat()

        if direction in ("down", "both") and -change >= threshold:
            last_event = (timestamp, "drop", round(-change, 5))

        elif direction in ("up", "both") and change >= threshold:
            last_event = (timestamp, "rise", round(change, 5))

    event_found = last_event is not None
    return event_found, last_event

def run_sentiment_analysis() -> Dict:
    """Lue analyysidata, laske sentimenttibias ja tallenna se lokiin."""
    log_path = CONFIG["analysis_log_path"]

    # Lue olemassa oleva analyysidata
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            data = [json.loads(line) for line in f if line.strip()]
    else:
        data = []

    # Suorita analyysi
    result = compute_bias(data, time_window_hours=24.0)

    # Tarkista, löytyykö trendimuutosta
    found, event = detect_trend_shifts(
        metric="broad_bias",
        window=3,
        threshold=0.02,
        direction="both"
    )

    # Kirjaa tulos sentimenttilokiin, mukaan lukien trendimuutostieto
    log_sentiment_result(result, trend_event=event if found else None)

    return result