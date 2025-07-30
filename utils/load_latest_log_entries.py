# utils/load_latest_log_entries.py
# logs = load_latest_log_entries("mylog.jsonl", limit=5, use_timestamp=True)





import json
import os
from typing import List, Dict
from datetime import datetime
from dateutil import parser as date_parser  # Requires python-dateutil

def load_latest_log_entries(
    file_path: str,
    limit: int = 10,
    use_timestamp: bool = False,
    timestamp_key: str = "timestamp"
) -> List[Dict]:
    """
    Load the latest entries from a JSON or JSONL log file.

    Parameters:
        file_path (str): Path to the log file (.json or .jsonl).
        limit (int): Number of latest entries to return.
        use_timestamp (bool): Whether to sort entries by ISO 8601 timestamp.
        timestamp_key (str): Key to use for timestamp sorting (used only if use_timestamp is True).

    Returns:
        List[dict]: List of log entries (each as a dictionary).
    """

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Log file not found: {file_path}")

    entries: List[Dict] = []

    # Read entries from JSON or JSONL
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
                    raise ValueError("JSON file must contain a list of entries.")
        else:
            raise ValueError("Unsupported file type. Only .json and .jsonl are supported.")
    except Exception as e:
        raise RuntimeError(f"Failed to read log file: {e}")

    # Sort by timestamp if requested
    if use_timestamp:
        def parse_ts(entry):
            try:
                return date_parser.isoparse(entry[timestamp_key])
            except Exception:
                return datetime.min  # fallback to sortable minimal value if timestamp is invalid

        entries = [e for e in entries if timestamp_key in e]
        entries.sort(key=parse_ts, reverse=True)

    return entries[-limit:] if not use_timestamp else entries[:limit]
