# modules/history_data_collector/history_data_collector.py
# version 2.0, aug 2025

import json
from typing import List
from utils.get_timestamp import get_timestamp
from utils.get_symbols_to_use import get_symbols_to_use
from utils.load_configs_and_logs import load_configs_and_logs
from modules.history_data_collector.utils import get_data_from_logs
from modules.save_and_validate.save_and_validate import save_and_validate
from modules.history_data_collector.collector_data_processor import collector_data_processor

def history_data_collector(symbols: List[str], history_config):

    print(f"\n💡 Found {len(symbols)} symbols to process...")

    collector_logs, ohlcv_logs, price_logs, log_path, log_schema_path = get_data_from_logs(symbols, history_config)
    all_collected_data = []

    for symbol in symbols:

        print(f"\n⚙️  Symbol: {symbol}")

        collector_entry = collector_logs.get(symbol, [])
        ohlcv_entry = ohlcv_logs.get(symbol, [])
        price_entry = price_logs.get(symbol, [])

        col_ts = collector_entry.get("timestamp") if collector_entry else None
        ohlcv_ts = ohlcv_entry.get("timestamp") if ohlcv_entry else None
        price_ts = price_entry.get("timestamp") if price_entry else None

        if (
            ohlcv_ts is not None
            and price_ts is not None
            and (
                col_ts is None
                or (
                    col_ts < ohlcv_ts
                    and col_ts < price_ts
                )
            )
        ):
            print(f"💹 Continuing the process for the symbol {symbol}")

            collected_data = collector_data_processor(
                symbol, history_config, ohlcv_entry, price_entry
            )
            all_collected_data.append(collected_data)

        else:
            print(f"⏭ Skipping {symbol} — data is up-to-date or missing required OHLCV/price timestamps")

    print("\n")

    # Save results to log
    print(f"❇️  Saving new result to {log_path}\n")
    save_and_validate(
        data=all_collected_data,
        path=log_path,
        schema=log_schema_path,
        verbose=False
    )

    return all_collected_data

if __name__ == "__main__":

    print(f"\nRunning History Data Collector...\n")
 
    configs_and_logs = load_configs_and_logs([
        {
            "name": "symbol",
            "mid_folder": "analysis",
            "module_key": "symbol_data_fetcher",
            "extension": ".jsonl",
            "return": ["config", "full_log_path", "full_log_schema_path"]
        },
        {
            "name": "history",
            "mid_folder": "analysis",
            "module_key": "history_analyzer",
            "extension": ".json",
            "return": ["config"]
        }
    ])

    # Vastaa alkuperäisen koodin muuttujia
    symbol_log_path = configs_and_logs["symbol_full_log_path"]
    symbol_config = configs_and_logs["symbol_config"]
    history_config = configs_and_logs["history_config"]

    result = get_symbols_to_use(symbol_config, symbol_log_path)
    all_symbols = result["all_symbols"]

    collected_data = history_data_collector(all_symbols, history_config)
    # print(f"\nCollected_data: {collected_data}")