import os
import json
from datetime import datetime
import pytz

def log_equity_if_blocked(result: dict, status: dict):
    
    if not status.get("block_trades"):
        return

    log_dir = "../AI-crypto-trader-logs/analysis-data"
    log_file = os.path.join(log_dir, "equity_manager_log.jsonl")

    os.makedirs(log_dir, exist_ok=True)

    # Lisää aikaleima Helsingin ajassa
    helsinki_time = datetime.now(pytz.timezone("Europe/Helsinki")).isoformat()
    result_with_timestamp = {"timestamp": helsinki_time, **result}

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(result_with_timestamp) + "\n")
