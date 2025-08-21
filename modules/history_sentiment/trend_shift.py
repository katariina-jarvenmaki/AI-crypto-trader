# modules/history_sentiment/trend_shift.py
# version 2.0, aug 2025

# import json
# import pandas as pd
# from datetime import datetime, timedelta

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

    print(f"=== Current data ===")
    print(f"bias_results: {bias_results}")
    print(f"entries: {entries}")
    print(f"config: {config}")
    print(f"combine_cfg: {combine_cfg}")
    print(f"method: {method}")
    print(f"keys: {keys}")
    print(f"weights: {weights}")
    print(f"bias values: {values}")
    print(f"combined_bias: {combined_bias}")



#     shift_cfg = config.get("trend_shift", {})

#     metric = shift_cfg.get("metric", "broad_bias")
#     if metric == "broad_bias":
#         metric = "broad-sentiment.bias"
#     elif metric == "hour_bias":
#         metric = "hour-sentiment.bias"

#     found, direction, change = detect_trend_shifts(
#         entries=entries,
#         metric=metric,
#         threshold=shift_cfg.get("threshold", 0.02),
#         direction=shift_cfg.get("direction", "both"),
#         lookback_minutes=shift_cfg.get("lookback_minutes", 15)
#     )

#     if combined_bias is not None:
#         print(f"✅ Trend Reversal Analysis complete")
#     else:
#         print(f"❌ Trend Reversal Analysis failed")
# 
#     return {
#         "combined_bias": combined_bias,
#         "direction": direction,
#         "change": change
#     }

# def detect_trend_shifts(
#     entries: list,
#     metric: str = "broad-sentiment.bias",
#     threshold: float = 0.02,
#     direction: str = "both",
#     lookback_minutes: int = 15
# ):

#     if not entries:
#         return False, None, None

#     parsed_entries = []
#     for item in entries:
#         if isinstance(item, str):
#             item = item.strip()
#             if not item:
#                 continue
#             try:
#                 parsed_entries.append(json.loads(item))
#             except json.JSONDecodeError:
#                 continue
#         elif isinstance(item, dict):
#             parsed_entries.append(item)
#         else:
#             continue

#     if not parsed_entries:
#         return False, None, None

#     def get_nested_value(d, path: str):
#         keys = path.split(".")
#         for k in keys:
#             if isinstance(d, dict) and k in d:
#                 d = d[k]
#             else:
#                 return None
#         return d

#     df = pd.DataFrame([
#         {
#             "timestamp": datetime.fromisoformat(item["timestamp"]),
#             metric: get_nested_value(item, metric)
#         }
#         for item in parsed_entries
#         if get_nested_value(item, metric) is not None
#     ])
# 
#     if df.empty:
#         return False, None, None

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
