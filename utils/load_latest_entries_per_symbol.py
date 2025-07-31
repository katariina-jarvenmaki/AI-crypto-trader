# utils/load_latest_log_entries.py

import os
import json
from typing import List, Dict, Optional
from dateutil import parser as date_parser
from collections import defaultdict
from datetime import timedelta

def get_latest_entries_per_symbol(symbols, file_path, max_age_minutes=60):
    end_time = get_timestamp()
    start_time = (date_parser.isoparse(end_time) - timedelta(minutes=max_age_minutes)).isoformat()

    all_entries = load_latest_log_entries(
        file_path=file_path,
        limit=10000,  # iso raja, koska suodatetaan jälkeenpäin
        use_timestamp=True,
        symbols=symbols,
        start_time=start_time,
        end_time=end_time,
    )

    latest_by_symbol = {}

    for entry in all_entries:
        symbol = entry.get("symbol")
        ts = date_parser.isoparse(entry.get("timestamp", ""))
        if not symbol:
            continue

        if symbol not in latest_by_symbol or ts > date_parser.isoparse(latest_by_symbol[symbol]["timestamp"]):
            latest_by_symbol[symbol] = entry

    return list(latest_by_symbol.values())

if __name__ == "__main__":

    file_path = "../AI-crypto-trader-logs/_TEST/fetch_logs/multi_ohlcv_fetch_log.jsonl"
    limit = 1
    use_timestamp=True
    symbols = ["BTCUSDT", "ETHUSDT"]
    end_time = get_timestamp()
    start_time = (date_parser.isoparse(end_time) - timedelta(hours=48)).isoformat()
    logs = load_latest_log_entries(
        file_path=file_path,
        limit=limit,
        use_timestamp=use_timestamp,
        symbols=symbols,
        start_time=start_time,
        end_time=end_time
    )
    print(logs)
