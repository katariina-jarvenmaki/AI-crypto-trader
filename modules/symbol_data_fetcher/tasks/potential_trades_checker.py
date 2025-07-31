
from pathlib import Path
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from utils.get_timestamp import get_timestamp 
from modules.pathbuilder.pathbuilder import pathbuilder
from modules.symbol_data_fetcher.utils import get_latest_entry
from modules.load_and_validate.load_and_validate import load_and_validate
from modules.symbol_data_fetcher.analysis_summary import analyze_all_symbols
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback

def print_and_save_recommendations(latest_entries, module_config, module_log_path, module_scheme_path):
    long_syms, short_syms, scores = analyze_all_symbols(latest_entries, module_config)
    
    print(f"latest_entries: {latest_entries}")
    print(f"module_log_path: {module_log_path}")
    print(f"module_scheme_path: {module_scheme_path}")

def needs_update(symbol: str, latest_entry: dict, max_age_minutes: int = 60) -> bool:

    try:
        if not isinstance(latest_entry, dict):
            raise TypeError("latest_entry is not a dict")

        if latest_entry.get("symbol") != symbol or "timestamp" not in latest_entry:
            return True

        current_ts = date_parser.isoparse(get_timestamp())
        latest_ts = date_parser.isoparse(latest_entry["timestamp"])
        age = current_ts - latest_ts
        return age > timedelta(minutes=max_age_minutes)

    except Exception as e:
        print(f"⚠️  Error while checking update need for {symbol}: {e}")
        return True

def get_symbols_to_scan():
    return [
        s for s in module_config["supported_symbols"]
        if s not in module_config["main_symbols"] and s not in module_config["blocked_symbols"]
    ]

def run_potential_trades_checker(general_config, module_config, module_log_path, module_scheme_path):

    symbols_to_process = get_symbols_to_scan()
    log_paths = pathbuilder(extension=".jsonl", file_name=general_config["module_filenames"]["symbol_data_fetcher"], mid_folder="analysis")
    temporary_path = Path(log_paths["logs_path"]) / module_config['task_config']['potential']['temp_log']
    schema_path = paths["schemas_path"]
    timestamp = get_timestamp()
    
    print(f"🔍 Scanning {len(symbols_to_process)} symbols at {timestamp}")

    for symbol in symbols_to_process:
        print(f"\n🔁 Checking symbol: {symbol}")

        latest_entries = get_latest_entry(symbol, temporary_path, max_age_minutes=module_config["ohlcv_max_age_minutes"])

        if needs_update(symbol, latest_entries, max_age_minutes=module_config["ohlcv_max_age_minutes"]):
            print(f"🚀 Fetching new OHLCV data: {symbol}")
            fetch_ohlcv_fallback(
                symbol=symbol,
                intervals=module_config["intervals"],
                limit=module_config["ohlcv_fetch_limit"],
                log_path=str(temporary_path)
            )
        else:
            hours = module_config["ohlcv_max_age_minutes"] // 60
            minutes = module_config["ohlcv_max_age_minutes"] % 60
            age_str = f"{hours}h {minutes}min" if hours else f"{minutes}min"
            print(f"✅ Fresh data already exists (less than {age_str} old): {symbol}")

    latest_entries = get_latest_entry(symbol, temporary_path, max_age_minutes=module_config["ohlcv_max_age_minutes"])

    print_and_save_recommendations(latest_entries, module_config, module_log_path, module_scheme_path)

    # empty temp file

if __name__ == "__main__":

    general_config = load_and_validate()
    paths = pathbuilder(extension=".json", file_name=general_config["module_filenames"]["symbol_data_fetcher"], mid_folder="analysis")
    module_log_path = paths["full_log_path"]
    module_scheme_path = paths["full_log_schema_path"]

    module_config = load_and_validate(file_path=paths["full_config_path"], schema_path=paths["full_config_schema_path"])
    
    log_paths = pathbuilder(extension=".jsonl", file_name=general_config["module_filenames"]["multi_interval_ohlcv"], mid_folder="fetch")
    # ohlcv_log_path = log_paths["full_log_path"]

    run_potential_trades_checker(general_config, module_config, module_log_path, module_scheme_path)
