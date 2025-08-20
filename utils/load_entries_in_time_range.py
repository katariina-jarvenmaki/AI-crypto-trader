# utils/load_entries_in_time_range.py
# version 2.0, aug 2025

import os
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from utils.get_timestamp import get_timestamp
from utils.load_latest_entry import load_latest_entry

def load_entries_in_time_range(
    file_path: str,
    symbols: Optional[List[str]] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> Dict[str, List[Dict]]:

    now = date_parser.isoparse(get_timestamp())

    if end_time is None:
        end_time = now.isoformat()

    if start_time is None:
        start_time = (now - timedelta(hours=24)).isoformat()

    results: Dict[str, List[Dict]] = {}

    if symbols:
        for sym in symbols:

            try:
                entries = load_latest_entry(
                    file_path=file_path,
                    use_timestamp=True,
                    symbol=sym,
                    start_time=start_time,
                    end_time=end_time,
                    limit=999999
                )
                if entries:
                    results[sym] = entries
            except ValueError:
                results[sym] = []
    else:
        entries = load_latest_entry(
            file_path=file_path,
            use_timestamp=True,
            start_time=start_time,
            end_time=end_time,
            limit=999999
        )
        for entry in entries:
            sym = entry.get("symbol", "UNKNOWN")
            results.setdefault(sym, []).append(entry)

    return results

if __name__ == "__main__":
    file_path = "../AI-crypto-trader-logs/_TEST/fetch_logs/multi_ohlcv_fetch_log.jsonl"
    symbols = ["BTCUSDT", "ETHUSDT"]

    start_time = "2025-08-19T12:00:00Z"
    end_time   = "2025-08-20T12:00:00Z"

    logs = load_entries_in_time_range(
        file_path=file_path,
        symbols=symbols,
        start_time=start_time,
        end_time=end_time
    )

    import json
    print(json.dumps(logs, indent=2))
