# modules/history_analyzer/history_analyzer.py

import json
from typing import List
from modules.history_analyzer.config_history_analyzer import CONFIG

def process_log_entry(entry: dict):
    print(f"ENTRY: {entry}")

def process_latest_entries_for_symbols(symbols: List[str]):
    seen = set()
    price_data_entries = get_latest_price_data_for_symbols(symbols)

    with open(CONFIG["ohlcv_log_path"], "r") as f:
        for line in reversed(f.readlines()):
            try:
                entry = json.loads(line.strip())
                symbol = entry.get("symbol")

                if symbol in symbols and symbol not in seen:
                    price_entry = price_data_entries.get(symbol)
                    if price_entry:
                        # Päivitetään OHLCV-entryn data_preview:iin hintadata:
                        entry["data_preview"]["price_data"] = price_entry["data_preview"]
                    process_log_entry(entry)  # nyt se käyttää rikastettua entryä
                    seen.add(symbol)

                if len(seen) == len(symbols):
                    break
            except Exception as e:
                print(f"Skipping invalid OHLCV line: {e}")

def get_latest_price_data_for_symbols(symbols: List[str]) -> dict:
    """
    Palauttaa dictin muodossa viimeisimmän price data -rivin per symbol.
    """
    latest = {}
    with open(CONFIG["price_log_path"], "r") as f:
        for line in reversed(f.readlines()):
            try:
                entry = json.loads(line.strip())
                symbol = entry.get("symbol")
                if symbol in symbols and symbol not in latest:
                    latest[symbol] = entry
                if len(latest) == len(symbols):
                    break
            except Exception as e:
                print(f"Skipping invalid PRICE line: {e}")
    return latest

def convert_price_log_entry_to_ohlcv_format(entry):
    """
    Convert price_data_log.jsonl format into a format expected by process_log_entry
    """
    symbol = entry.get("symbol")
    timestamp = entry.get("timestamp")
    data_preview = {
        "1m": {
            "close": entry["data_preview"].get("last_price")
        },
        "1d": {
            "volume": entry["data_preview"].get("volume"),
            "change_24h": entry["data_preview"].get("price_change_percent")
        }
    }

    return {
        "symbol": symbol,
        "timestamp": timestamp,
        "data_preview": data_preview
    }

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
    process_latest_entries_for_symbols(symbols)

if __name__ == "__main__":
    main()