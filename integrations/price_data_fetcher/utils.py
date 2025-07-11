# integrations/price_data_fetcher/utils.py

import os
import json
from typing import List
from datetime import datetime

from integrations.price_data_fetcher.config_price_data_fetcher import CONFIG
from configs.config import LOCAL_TIMEZONE

def ensure_log_file_exists(log_path: str):
    if not os.path.exists(log_path):
        print(f"📄 Creating log file: {log_path}")
        with open(log_path, "w") as f:
            f.write("")

def append_to_log(log_path: str, symbol: str, exchange: str, data: dict):
    timestamp = datetime.now(LOCAL_TIMEZONE).isoformat()

    log_entry = {
        "timestamp": timestamp,
        "source_exchange": exchange.capitalize() if exchange else "unknown",
        "symbol": symbol,
        "data_preview": {
            "last_price": data.get("lastPrice"),
            "price_change_percent": data.get("priceChangePercent"),
            "high_price": data.get("highPrice"),
            "low_price": data.get("lowPrice"),
            "volume": data.get("volume"),
            "turnover": data.get("turnover")
        }
    }

    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    print(f"✅ Logged {symbol} from {exchange} at {timestamp}")

def trim_log_file(log_path: str, max_lines: int):
    with open(log_path, "r") as f:
        lines = f.readlines()

    if len(lines) > max_lines:
        print(f"✂️  Trimming log file from {len(lines)} to {max_lines}")
        with open(log_path, "w") as f:
            f.writelines(lines[-max_lines:])

def get_latest_symbols_from_log(file_path: str) -> List[str]:

    with open(file_path, "r") as f:
        lines = f.readlines()
        if not lines:
            return []
        last_entry = json.loads(lines[-1])

        combined_symbols = set()
        for key in CONFIG["symbol_keys"]:
            combined_symbols.update(last_entry.get(key, []))

        return list(combined_symbols)

def test_single_exchange(symbol, exchange_name):
    fetcher = PriceDataFetcher(symbol=symbol, order=[exchange_name])
    data = fetcher.fetch()
    print(f"[TEST] Data from {exchange_name}:", data)