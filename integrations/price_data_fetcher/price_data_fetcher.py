# integrations/price_data_fetcher/price_data_fetcher.py

import json
from typing import List

from integrations.price_data_fetcher.config_price_data_fetcher import CONFIG

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

    print("Running a price data fetcher...")

    symbols = get_latest_symbols_from_log(CONFIG["symbol_log_path"])

    if not symbols:
       print("No symbols found in latest symbol log.")
       return
    print(f"Found {len(symbols)} symbols to process...")

    # seen = set()
    # with open(ohlcv_log_path, "r") as f:
    #     for line in reversed(f.readlines()):
    #         try:
    #             entry = json.loads(line.strip())
    #             symbol = entry.get("symbol")
    #             if symbol in symbols and symbol not in seen:
    #                 process_log_entry(entry)
    #                 seen.add(symbol)
    #             if len(seen) == len(symbols):
    #                 break
    #         except Exception as e:
    #             print(f"Skipping invalid OHLCV line: {e}")

if __name__ == "__main__":
    main()