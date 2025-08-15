# utils/load_latest_entry.py
# version 2.0, aug 2025

import os
import json
from typing import List, Dict, Optional
from dateutil import parser as date_parser
from datetime import datetime, timedelta

def load_latest_entry(
    file_path,
    limit: int = 10,
    use_timestamp: bool = False,
    symbol: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> List[Dict]:

    if not isinstance(file_path, str):
        file_path = str(file_path)

    if not os.path.isfile(file_path):
        return []

    entries: List[Dict] = []

    # Parse time filters
    start_dt = date_parser.isoparse(start_time) if start_time else None
    end_dt = date_parser.isoparse(end_time) if end_time else None

    # Read entries from file
    try:
        if file_path.endswith(".jsonl"):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        elif file_path.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    entries = data
                else:
                    raise ValueError("❌ JSON file must contain a list of entries.")
        else:
            raise ValueError("❌ Unsupported file type. Only .json and .jsonl are supported.")
    except Exception as e:
        raise RuntimeError(f"❌ Failed to read log file: {e}")

    # Filter by symbol
    if symbol is not None:
        symbol_key = "symbol"

        if not entries:
            return []

        if symbol_key not in entries[0]:
            raise ValueError(f"Expected key '{symbol_key}' not found in log entries.")

        entries = [e for e in entries if e.get(symbol_key) == symbol]

    # Filter by time range
    timestamp_key = "timestamp"
    if start_dt or end_dt:
        def is_within_time_range(entry):
            try:
                ts = date_parser.isoparse(entry[timestamp_key])
                if start_dt and ts < start_dt:
                    return False
                if end_dt and ts > end_dt:
                    return False
                return True
            except Exception:
                return False

        entries = [e for e in entries if timestamp_key in e and is_within_time_range(e)]

    # Optional: Sort by timestamp
    if use_timestamp:
        def parse_ts(entry):
            try:
                return date_parser.isoparse(entry[timestamp_key])
            except Exception:
                return datetime.min

        entries.sort(key=parse_ts, reverse=True)

    return entries[-limit:] if not use_timestamp else entries[:limit]

# Example usage
if __name__ == "__main__":
    def get_timestamp():
        return datetime.utcnow().isoformat()

    file_path = "../AI-crypto-trader-logs/_TEST/fetch_logs/multi_ohlcv_fetch_log.jsonl"
    limit = 2
    use_timestamp = True
    symbol = "BTCUSDT"
    end_time = get_timestamp()
    start_time = (date_parser.isoparse(end_time) - timedelta(hours=48)).isoformat()
    
    logs = load_latest_entry(
        file_path=file_path,
        limit=limit,
        use_timestamp=use_timestamp,
        symbol=symbol,
        start_time=start_time,
        end_time=end_time
    )
    print(logs)
