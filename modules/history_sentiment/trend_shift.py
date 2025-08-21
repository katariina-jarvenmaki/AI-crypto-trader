# modules/history_sentiment/trend_shift.py
# version 2.0, aug 2025

import json
import pandas as pd
from dateutil.parser import isoparse
from datetime import datetime, timedelta
from utils.get_timestamp import get_timestamp

def trend_shift_analyzer(bias_results: dict, entries: list, config: dict):

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
            if not isinstance(d, dict):   
                safeguard
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

    broad_bias = bias_results['broad-sentiment']['bias']
    found, direction, change = detect_trend_shifts(
        old_biases=entries,
        current_bias=broad_bias,
        metric=metric,
        threshold=shift_cfg.get("threshold", 0.02),
        direction=shift_cfg.get("direction", "both"),
        lookback_minutes=shift_cfg.get("lookback_minutes", 15)
    )

    if found:
        print(f"✅ Trend Shift Analysis complete")
    else:
        print(f"❌ Trend Shift Analysis failed")

    return {
        "combined_bias": combined_bias,
        "direction": direction,
        "change": change
    }

def detect_trend_shifts(
    old_biases: list,
    current_bias: dict,
    metric: str = "broad-sentiment.bias",
    threshold: float = 0.02,
    direction: str = "both",
    lookback_minutes: int = 15
):
    """
    Detecting Trend Shifts:
     * Compares the current bias with the oldest available bias
       within the lookback window from old_biases.
    """

    if not old_biases:
        print("⚠️  No previous data found for Trend Shift Analysis")
        return False, None, None

    def get_nested_value(d, path: str):
        keys = path.split(".")
        for k in keys:
            if isinstance(d, dict) and k in d:
                d = d[k]
            else:
                return None
        return d

    parsed_old_biases = []
    for item in old_biases:
        if isinstance(item, str):
            try:
                parsed_old_biases.append(json.loads(item))
            except json.JSONDecodeError:
                continue
        elif isinstance(item, dict):
            parsed_old_biases.append(item)

    if not parsed_old_biases:
        print("⚠️  [ERROR]: Parsing old biases from History Sentiment -log failed!")
        return False, None, None

    df = pd.DataFrame([
        {
            "timestamp": datetime.fromisoformat(item["timestamp"]),
            metric: get_nested_value(item, metric)
        }
        for item in parsed_old_biases
        if get_nested_value(item, metric) is not None
    ])

    if df.empty:
        print("⚠️  [ERROR]: Empty DataFrame after parsing old_biases!")
        return False, None, None

    curr_time = isoparse(get_timestamp())
    cutoff_time = curr_time - timedelta(minutes=lookback_minutes)
    df_window = df[df["timestamp"] >= cutoff_time]

    if df_window.empty:
        print("⚠️  No old_biases found within lookback window")
        return False, None, None

    df_window.sort_values("timestamp", inplace=True)
    old_bias = df_window[metric].iloc[0]

    print(f"df_window: {df_window}")
    print(f"old_bias: {old_bias}")
    print(f"current_bias: {current_bias}")

#     df.sort_values("timestamp", inplace=True)
#     df.reset_index(drop=True, inplace=True)

#     cutoff_time = df["timestamp"].max() - timedelta(minutes=lookback_minutes)
#     df_recent = df[df["timestamp"] >= cutoff_time]

#     if len(df_recent) < 2:
#         return False, None, None

#     start_val = df_recent[metric].iloc[0]
#     end_val = df_recent[metric].iloc[-1]
#     change = end_val - start_val
#     print(f"start_val: {start_val}")
#     print(f"end_val: {end_val}")
#     print(f"change: {change}")

#     if direction in ("down", "both") and -change >= threshold:
#         return True, "drop", round(-change, 5)
#     elif direction in ("up", "both") and change >= threshold:
#         return True, "rise", round(change, 5)
#     else:
#         return False, None, None
