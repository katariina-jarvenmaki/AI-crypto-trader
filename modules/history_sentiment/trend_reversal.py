# modules/history_sentiment/trend_reversal.py
# version 2.1, aug 2025

import json
import pandas as pd
from datetime import datetime, timedelta

def trend_reversal_analyzer(bias_results: dict, entries: list, config: dict):

    combine_cfg = config.get("combine_bias", {})
    method = combine_cfg.get("method", "average")
    keys = combine_cfg.get("keys", [])
    weights = combine_cfg.get("weights", [])

    values = []
    if bias_results is None:
        bias_results = {}

    for k in keys:
        parts = k.split(".")
        d = bias_results
        for p in parts:
            if not isinstance(d, dict):   # safeguard
                d = {}
                break
            d = d.get(p, {})
        if isinstance(d, (int, float)):
            values.append(d)

    combined_bias = None
    if values:
        if method == "average":
            combined_bias = round(sum(values) / len(values), 3)
        elif method == "weighted" and weights and len(weights) == len(values):
            total = sum(w * v for w, v in zip(weights, values))
            combined_bias = round(total / sum(weights), 3)
        elif method == "last":
            combined_bias = round(values[-1], 3)

    shift_cfg = config.get("trend_shift", {})

    metric = shift_cfg.get("metric", "broad_bias")
    if metric == "broad_bias":
        metric = "broad-sentiment.bias"
    elif metric == "hour_bias":
        metric = "hour-sentiment.bias"

    found, event = detect_trend_shifts(
        entries=entries,
        metric=metric,
        threshold=shift_cfg.get("threshold", 0.02),
        direction=shift_cfg.get("direction", "both"),
        lookback_minutes=shift_cfg.get("lookback_minutes", 15)
    )

    if combined_bias is not None or found is not None or event is not None:
        print(f"✅ Trend Reversal Analysis complete")
    else:
        print(f"❌ Trend Reversal Analysis failed")

    return {
        "combined_bias": combined_bias,
        "found": found,
        "event": event,
    }


def detect_trend_shifts(
    entries: list,
    metric: str = "broad-sentiment.bias",
    threshold: float = 0.02,
    direction: str = "both",
    lookback_minutes: int = 15
):

    if not entries:
        return False, None

    parsed_entries = []
    for item in entries:
        if isinstance(item, str):
            item = item.strip()
            if not item:
                continue
            try:
                parsed_entries.append(json.loads(item))
            except json.JSONDecodeError:
                continue
        elif isinstance(item, dict):
            parsed_entries.append(item)
        else:
            continue

    if not parsed_entries:
        return False, None

    df = pd.DataFrame([
        {
            "timestamp": datetime.fromisoformat(item["timestamp"]),
            metric: item.get("result", {}).get(metric)
        }
        for item in parsed_entries
        if "result" in item and metric in item["result"]
    ])

    if df.empty:
        return False, None

    df.sort_values("timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)

    cutoff_time = df["timestamp"].max() - timedelta(minutes=lookback_minutes)
    df_recent = df[df["timestamp"] >= cutoff_time]

    if len(df_recent) < 2:
        return False, None

    start_val = df_recent[metric].iloc[0]
    end_val = df_recent[metric].iloc[-1]
    change = end_val - start_val
    timestamp = df_recent["timestamp"].iloc[0].isoformat()

    if direction in ("down", "both") and -change >= threshold:
        return True, (timestamp, "drop", round(-change, 5))
    elif direction in ("up", "both") and change >= threshold:
        return True, (timestamp, "rise", round(change, 5))
    else:
        return False, None
