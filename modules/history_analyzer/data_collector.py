# modules/data_collector/data_collector.py

import json
from typing import Dict, List
from modules.history_analyzer.config_history_analyzer import CONFIG

def parse_log_entry(entry: dict) -> Dict:
    symbol = entry["symbol"]
    timestamp = entry["timestamp"]

    price_data = entry["data_preview"].get("price_data", {})
    price = price_data.get("last_price")
    change_24h = price_data.get("price_change_percent")
    high_price = price_data.get("high_price")
    low_price = price_data.get("low_price")
    volume = price_data.get("volume")
    turnover = price_data.get("turnover")

    rsi_data = {
        interval: entry["data_preview"].get(interval, {}).get("rsi")
        for interval in CONFIG["intervals_to_use"]
    }
    ema_data = {
        interval: entry["data_preview"].get(interval, {}).get("ema")
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
    bb_upper = {
        interval: entry["data_preview"].get(interval, {}).get("bb_upper")
        for interval in CONFIG["intervals_to_use"]
    }
    bb_lower = {
        interval: entry["data_preview"].get(interval, {}).get("bb_lower")
        for interval in CONFIG["intervals_to_use"]
    }

    return {
        "symbol": symbol,
        "timestamp": timestamp,
        "price": price,
        "change_24h": change_24h,
        "high_price": high_price,
        "low_price": low_price,
        "volume": volume,
        "turnover": turnover,
        "rsi": rsi_data,
        "ema": ema_data,
        "macd": macd_data,
        "macd_signal": signal_data,
        "bb_upper": bb_upper,
        "bb_lower": bb_lower
    }

def get_latest_price_data_for_symbols(symbols: List[str]) -> dict:
    latest = {}
    with open(CONFIG["price_log_path"], "r") as f:
        for line in reversed(f.readlines()):
            stripped = line.strip()
            if not stripped or '\x00' in stripped:
                continue
            try:
                entry = json.loads(stripped)
                symbol = entry.get("symbol")
                if symbol in symbols and symbol not in latest:
                    latest[symbol] = entry
                if len(latest) == len(symbols):
                    break
            except Exception as e:
                print(f"Skipping invalid PRICE line:\n  Raw: {repr(line)}\n  Error: {e}")

    return latest

def data_collector(symbols: List[str]):
    seen = set()
    parsed_entries = []
    price_data_entries = get_latest_price_data_for_symbols(symbols)

    with open(CONFIG["ohlcv_log_path"], "r") as f:
        for line in reversed(f.readlines()):
            try:
                entry = json.loads(line.strip())
                symbol = entry.get("symbol")

                if symbol in symbols and symbol not in seen:
                    price_entry = price_data_entries.get(symbol)
                    if price_entry:
                        entry["data_preview"]["price_data"] = price_entry["data_preview"]
                    parsed = parse_log_entry(entry)
                    parsed_entries.append(parsed)
                    seen.add(symbol)

                if len(seen) == len(symbols):
                    break

            except Exception as e:
                print(f"Skipping invalid OHLCV line: {e}")

    return parsed_entries
