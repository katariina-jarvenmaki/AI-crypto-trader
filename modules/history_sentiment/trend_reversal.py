# modules/history_sentiment/trend_reversal.py
# version 2.0, aug 2025

import json
import pandas as pd
from datetime import datetime, timedelta
from utils.load_entries_in_time_range import load_entries_in_time_range

def trend_reversal_analyzer(bias_24h, bias_1h, entries):

    broad_bias = bias_24h.get("bias", 0)
    hour_bias = bias_1h.get("bias", 0)
    combined_bias = round((broad_bias + hour_bias) / 2.0, 3)

    found, event = detect_trend_shifts(
        entries=entries,
        metric="broad_bias", 
        threshold=0.02, 
        direction="both",
        lookback_minutes=15
    )

    if combined_bias is None or found is None or event is None:
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
    metric: str = "broad_bias",
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
            metric: item["result"].get(metric)
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

if __name__ == "__main__":

    bias_24h = {"bias": 0.3}
    bias_1h = {"bias": -0.1}

    log_path = "../AI-crypto-trader-logs/analysis_logs/history_sentiment_log.jsonl"
    all_symbols = {'NMRUSDT', 'BIOUSDT', 'VANAUSDT', 'ICPUSDT', 'ETCUSDT', 'XRPUSDT', 'AVAXUSDT', 'NEARUSDT', 'DASHUSDT', 'ENSUSDT', 'XLMUSDT', 'PAXGUSDT', 'CAKEUSDT', 'MOVRUSDT', 'ETHUSDT', 'TREEUSDT', 'GPSUSDT', 'LPTUSDT', 'ZECUSDT', 'BCHUSDT', 'TRBUSDT', 'SOLUSDT', 'BANANAUSDT', 'AEROUSDT', 'PENDLEUSDT', 'CTSIUSDT', 'ARCUSDT', 'RADUSDT', 'OMNIUSDT', 'APTUSDT', 'AUCTIONUSDT', 'TRUMPUSDT', 'LTCUSDT', 'XAUTUSDT', 'XMRUSDT', 'TIAUSDT', 'OGNUSDT', 'YFIUSDT', 'COOKUSDT', 'EGLDUSDT', 'ALUUSDT', 'DEXEUSDT', 'GRASSUSDT', 'LINKUSDT', 'AVAILUSDT', 'XTZUSDT', 'TAOUSDT', 'HYPEUSDT', 'SUSDT', 'CTCUSDT', 'HBARUSDT', 'BNBUSDT', 'ILVUSDT', 'KSMUSDT', 'QNTUSDT', 'QTUMUSDT', 'UNIUSDT', 'REDUSDT', 'FBUSDT', 'UMAUSDT', 'SUIUSDT', 'BTCUSDT', 'RUNEUSDT', 'LDOUSDT', 'CVXUSDT', 'METISUSDT', 'MEMEUSDT', 'DIAUSDT', 'MORPHOUSDT', 'OGUSDT', 'ADAUSDT', 'INJUSDT', 'BEAMUSDT', 'DOTUSDT', 'RENDERUSDT'}
    oldest_allowed = "2025-08-19T14:38:21.908610+03:00"
    newest_allowed = "2025-08-20T14:38:21.908610+03:00"

    entries = load_entries_in_time_range(
        file_path=log_path,
        symbols=all_symbols,
        start_time=oldest_allowed,
        end_time=newest_allowed
    )

    analysis = trend_reversal_analyzer(bias_24h, bias_1h, entries)
    # print(analysis)
