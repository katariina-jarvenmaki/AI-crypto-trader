# modules/symbol_data_fetcher/tasks/fetch_symbols_data.py
# version 2.0, aug 2025

from datetime import datetime, timedelta
from utils.get_timestamp import get_timestamp 
from utils.get_symbols_to_use import get_symbols_to_use
from utils.load_configs_and_logs import load_configs_and_logs
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback

def run_fetch_symbols_data(general_config, module_config, module_log_path, module_schema_path, ohlcv_log_path, ohlcv_schema_path):

    timestamp = get_timestamp()
    print(f"\n🕒 Running fetch at: {timestamp}\n")

    result = get_symbols_to_use(module_config, module_log_path)
    all_symbols = result["all_symbols"]
    message = result["message"]

    if message:
        print(f"\n{message}")

    print(f"\n🧮 Total unique symbols to process: {len(all_symbols)}\n")
    for symbol in sorted(all_symbols):
        print(f"➡️  Fetching {symbol}")
        fetch_ohlcv_fallback(
            symbol=symbol,
            intervals=module_config["intervals"],
            limit=module_config["ohlcv_fetch_limit"],
            log_path=str(ohlcv_log_path)
        )

if __name__ == "__main__":

    configs_and_logs = load_configs_and_logs([
        {
            "name": "symbol",
            "mid_folder": "analysis",
            "module_key": "symbol_data_fetcher",
            "extension": ".jsonl",
            "return": ["config", "logs_path", "full_log_path", "full_log_schema_path"]
        },
        {
            "name": "ohlcv",
            "mid_folder": "fetch",
            "module_key": "multi_interval_ohlcv",
            "extension": ".jsonl",
            "return": ["full_log_path", "full_log_schema_path"]
        }
    ])
    general_config = configs_and_logs.get("general_config")
    symbol_config = configs_and_logs.get("symbol_config")
    symbol_full_log_path = configs_and_logs.get("symbol_full_log_path")
    symbol_full_log_schema_path = configs_and_logs.get("symbol_full_log_schema_path")
    ohlcv_full_log_path = configs_and_logs.get("ohlcv_full_log_path")
    ohlcv_full_log_schema_path = configs_and_logs.get("ohlcv_full_log_schema_path")

    run_fetch_symbols_data(general_config, symbol_config, symbol_full_log_path, symbol_full_log_schema_path, ohlcv_full_log_path, ohlcv_full_log_schema_path)
