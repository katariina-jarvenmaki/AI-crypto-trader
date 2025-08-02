# modules/symbol_data_fetcher/tasks/fetch_symbols_data.py
# version 2.0, aug 2025

from datetime import datetime, timedelta
from utils.get_timestamp import get_timestamp 
from utils.get_symbols_to_use import get_symbols_to_use
from modules.pathbuilder.pathbuilder import pathbuilder
from modules.load_and_validate.load_and_validate import load_and_validate
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback

def run_fetch_symbols_data(general_config, module_config, module_log_path, module_schema_path, ohlcv_log_path, ohlcv_schema_path):

    timestamp = get_timestamp()
    print(f"🕒 Running fetch at: {timestamp}")

    result = get_symbols_to_use(module_config, module_log_path)
    symbols_to_use = result["symbols_to_use"]
    message = result["message"]

    if message:
        print(message)

    print(f"🧮 Total unique symbols to process: {len(symbols_to_use)}")
    for symbol in sorted(symbols_to_use):
        print(f"➡️  Fetching {symbol}")
        fetch_ohlcv_fallback(
            symbol=symbol,
            intervals=module_config["intervals"],
            limit=module_config["ohlcv_fetch_limit"],
            log_path=str(ohlcv_log_path)
        )

if __name__ == "__main__":

    general_config = load_and_validate()
    paths = pathbuilder(extension=".jsonl", file_name=general_config["module_filenames"]["symbol_data_fetcher"], mid_folder="analysis")
    module_log_path = paths["full_log_path"]
    module_schema_path = paths["full_log_schema_path"]

    module_config = load_and_validate(file_path=paths["full_config_path"], schema_path=paths["full_config_schema_path"])

    log_paths = pathbuilder(extension=".jsonl", file_name=general_config["module_filenames"]["multi_interval_ohlcv"], mid_folder="fetch")

    ohlcv_log_path = log_paths["full_log_path"]
    ohlcv_schema_path = log_paths["full_log_path"]

    run_fetch_symbols_data(general_config, module_config, module_log_path, module_schema_path, ohlcv_log_path, ohlcv_schema_path)

    
