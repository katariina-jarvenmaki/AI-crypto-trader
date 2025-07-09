# modules/history_analyzer/history_analyzer.py

import os
import sys
import json
import math
from pathlib import Path
from typing import Dict, List

from modules.history_analyzer.config_history_analyzer import CONFIG

def process_log_entry(entry: dict):
    parsed = parse_log_entry(entry)
    symbol = parsed["symbol"]
    timestamp = parsed["timestamp"]
    current_rsi = parsed["rsi"]
    macd = parsed["macd"]
    macd_signal = parsed["macd_signal"]
    macd_signal = parsed["macd_signal"]
    price_data = parsed["price_data"]

    print(f"\n🔍 Processing symbol: {symbol} @ {timestamp}")

    # Get 24h price change next
    print(f"symbol: {symbol}")
    print(f"timestamp: {timestamp}")
    print(f"current_rsi: {current_rsi}")
    print(f"macd: {macd}")
    print(f"macd_signal: {macd_signal}")   
    print(f"close (1m): {price_data.get('1m')}")

def parse_log_entry(entry: dict) -> Dict:

    symbol = entry["symbol"]
    timestamp = entry["timestamp"]
    
    rsi_data = {
        interval: entry["data_preview"].get(interval, {}).get("rsi")
        for interval in CONFIG["intervals_to_use"]
    }
    macd_data = {
        interval: entry["data_preview"].get(interval, {}).get("macd")
        for interval in CONFIG["intervals_to_use"]
    }
    signal_data = {
        interval: entry["data_preview"].get(interval, {}).get("macd_signal")
        for interval in CONFIG["intervals_to_use"]
    }
    price_data = {
        interval: entry["data_preview"].get(interval, {}).get("close")
        for interval in CONFIG["intervals_to_use"]
    }
    return {
        "symbol": symbol,
        "timestamp": timestamp,
        "rsi": rsi_data,
        "macd": macd_data,
        "macd_signal": signal_data,
        "price_data": price_data
    }

def process_latest_entries_for_symbols(symbols: List[str], ohlcv_log_path: str):

    seen = set()
    with open(ohlcv_log_path, "r") as f:
        for line in reversed(f.readlines()):
            try:
                entry = json.loads(line.strip())
                symbol = entry.get("symbol")
                if symbol in symbols and symbol not in seen:
                    process_log_entry(entry)
                    seen.add(symbol)
                if len(seen) == len(symbols):
                    break
            except Exception as e:
                print(f"Skipping invalid OHLCV line: {e}")

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

def main():

    symbols = get_latest_symbols_from_log(CONFIG["symbol_log_path"])

    if not symbols:
       print("No symbols found in latest symbol log.")
       return
    print(f"Found {len(symbols)} symbols to process...")
    process_latest_entries_for_symbols(symbols, CONFIG["ohlcv_log_path"])

if __name__ == "__main__":
    main()