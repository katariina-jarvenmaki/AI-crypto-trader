# integrations/multi_interval_ohlcv/re_fetch_from_log.py

import json
from multi_ohlcv_handler import fetch_ohlcv_fallback, LOG_FILE_PATH, analyze_ohlcv

def re_fetch_from_log(log_index=-1):
    """
    Re-fetches the same data based on a log entry and displays technical analysis.
    log_index: -1 for the latest fetch, 0 for the first, etc.
    """
    with open(LOG_FILE_PATH, "r") as f:
        log_entries = [json.loads(line) for line in f]

    if not log_entries:
        print("❌ No log entries found.")
        return None, None, None

    # Safe index lookup
    try:
        entry = log_entries[log_index]
    except IndexError:
        print(f"❌ Index {log_index} is not valid. There are {len(log_entries)} entries in the log.")
        return None, None, None

    print(f"\n🔁 Re-fetching symbol: {entry['symbol']} | Intervals: {entry['intervals']} | Source: {entry['source_exchange']}")
    print(f"🕒 Original timestamp: {entry['timestamp']}\n")

    data, source = fetch_ohlcv_fallback(
        symbol=entry["symbol"],
        intervals=entry["intervals"],
        limit=entry["limit"],
        start_time=entry["start_time"],
        end_time=entry["end_time"]
    )

    if not data:
        print("❌ Re-fetch failed.")
        return None, None, entry

    print(f"✅ Data re-fetched successfully ({source})\n")

    analysis_results = {}
    for interval, df in data.items():
        analysis = analyze_ohlcv(df)
        analysis_results[interval] = analysis

        print(f"📊 Interval: {interval}")
        for key, value in analysis.items():
            print(f"  {key.upper():<12}: {value}")
        print()

    return data, analysis_results, entry
