import os
import json
from typing import List, Dict, Optional
from dateutil import parser as date_parser
from collections import defaultdict
from utils.get_timestamp import get_timestamp 
from datetime import timedelta
from utils.load_latest_entry import load_latest_entry

def load_latest_entries_per_symbol(symbols, file_path, max_age_minutes=60):
    end_time = get_timestamp()
    start_time = (date_parser.isoparse(end_time) - timedelta(minutes=max_age_minutes)).isoformat()

    latest_by_symbol = {}

    for sym in symbols:
        entries = load_latest_entry(
            file_path=file_path,
            limit=1,
            use_timestamp=True,
            symbol=sym,
            start_time=start_time,
            end_time=end_time,
        )

        if entries:
            latest_by_symbol[sym] = entries[0]

    latest_entries = {
        entry["symbol"]: entry
        for entry in latest_by_symbol.values()
        if isinstance(entry, dict) and "symbol" in entry
    }

    return latest_entries

if __name__ == "__main__":
    file_path = "../AI-crypto-trader-logs/_TEST/analysis_logs/temporary_log_potential_trades.jsonl"
    symbols = ["USD1USDT", "CUSDT"]

    logs = load_latest_entries_per_symbol(
        symbols=symbols,
        file_path=file_path,
        max_age_minutes=600  # tai esim. 48*60 jos haluat kahden vuorokauden ikäisiä
    )

    print(json.dumps(logs, indent=2))
