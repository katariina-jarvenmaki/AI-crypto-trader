from datetime import datetime, timedelta
from utils.get_timestamp import get_timestamp 
from utils.load_latest_entry import load_latest_entry
from modules.pathbuilder.pathbuilder import pathbuilder
from modules.load_and_validate.load_and_validate import load_and_validate
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback

def fetch_symbols_data(general_config, module_config, module_log_path, module_schema_path, ohlcv_log_path, ohlcv_schema_path):

    timestamp = get_timestamp()
    print(f"🕒 Running fetch at: {timestamp}")

    symbol_keys = module_config['task_config']['potential']['symbol_keys']

    latest_entry = load_latest_entry(
        file_path=module_log_path,
        limit=1,
        use_timestamp=True
    )

    all_symbols = set()

    # Tarkista löytyikö logista mitään
    if latest_entry and isinstance(latest_entry, list) and isinstance(latest_entry[0], dict):
        entry = latest_entry[0]
        for key in symbol_keys:
            symbols = entry.get(key, [])
            if symbols:
                print(f"🔍 {key}: {symbols[:5]}... ({len(symbols)} total)")
            all_symbols.update(symbols)

    # Jos ei saatu symboleita logista → fallback main_symbols
    if not all_symbols:
        print("⚠️  No valid symbol data found in log. Falling back to module config's main_symbols")
        fallback_symbols = module_config.get("main_symbols", [])
        all_symbols.update(fallback_symbols)

    print(f"🧮 Total unique symbols to process: {len(all_symbols)}")
    for symbol in sorted(all_symbols):
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

    fetch_symbols_data(general_config, module_config, module_log_path, module_schema_path, ohlcv_log_path, ohlcv_schema_path)

    
