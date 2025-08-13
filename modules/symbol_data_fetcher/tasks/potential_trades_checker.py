# modules/symbol_data_fetcher/tasks/potential_trades_checker.py
# version 2.0, aug 2025

import os
import dateutil.parser
from pathlib import Path
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from utils.get_timestamp import get_timestamp 
from utils.load_configs_and_logs import load_configs_and_logs
from modules.save_and_validate.save_and_validate import save_and_validate
from modules.load_and_validate.load_and_validate import load_and_validate
from modules.symbol_data_fetcher.analysis_summary import analyze_all_symbols, prepare_analysis_results
from utils.load_latest_entries_per_symbol import load_latest_entries_per_symbol
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback
from utils.empty_the_file import empty_the_file

def print_and_save_recommendations(latest_entries, module_config, module_log_path, module_schema_path):
    
    long_syms, short_syms, scores = analyze_all_symbols(latest_entries, module_config)
    
    if not long_syms and not short_syms:
        print("😕 No analyzable data for today.")
        return

    print("\n🧠 Verbal interpretation:")

    for sym in long_syms:
        score = scores[sym]["score"]
        print(f" - {sym}: LONG bias (score: {score:.2f})")

    for sym in short_syms:
        score = scores[sym]["score"]
        print(f" - {sym}: SHORT bias (score: {score:.2f})")

    if long_syms:
        print("\n📈 💚 LONG RECOMMENDATIONS (most potential first):")
        print(" ".join(long_syms))

    if short_syms:
        print("\n📉 ❤️  SHORT RECOMMENDATIONS (most potential first):")
        print(" ".join(short_syms))

    # Save analysis log, if implemented elsewhere
    analysis_results = prepare_analysis_results(scores, module_config)

    print(f"\n💾 Saving new results, if not already in log...")

    # Check if it's already on log
    if os.path.exists(module_log_path):
        existing_data = load_and_validate(
            file_path=module_log_path,
            schema_path=module_schema_path
        )
        if existing_data is None:
            print("⚠️  Warning: Log exists but failed to load properly, initializing empty list.")
            existing_data = []
    else:
        print(f"❗ Log file not found: {module_log_path}. Initializing empty log.")
        existing_data = []

    # Check the last timestamp
    if existing_data:
        last_entry = existing_data[-1]
        last_timestamp_str = last_entry.get("timestamp")
        last_timestamp = dateutil.parser.isoparse(last_timestamp_str) if last_timestamp_str else None
    else:
        last_timestamp = None

    # Saving...
    for result in analysis_results:
        # print(f"🔍 Result type: {type(result)}, value: {result}")
        
        new_timestamp_str = result.get("timestamp")
        new_timestamp = dateutil.parser.isoparse(new_timestamp_str) if new_timestamp_str else None

        # Estetään tallennus jos alle tunti edellisestä
        min_interval = timedelta(hours=module_config.get("analysis_min_interval_hours", 1))
        if last_timestamp and new_timestamp and new_timestamp - last_timestamp < min_interval:
            print(f"⏱️  Skipping save — less than 1h since last log entry at {last_timestamp.isoformat()}\n")
            continue

        print(f"❇️  Saving new result: {new_timestamp.isoformat()}\n")
        save_and_validate(
            data=result,
            path=module_log_path,
            schema=module_schema_path,
            verbose=False
        )

    return True

def needs_update(symbol: str, latest_entry: dict, max_age_minutes: int) -> bool:

    if latest_entry is None:
        print(f"⚠️  No previous entry found for {symbol}")
        return True

    if not isinstance(latest_entry, dict):
        print(f"⚠️  Latest_entry is not a dict for {symbol}")
        return True

    try:
        if latest_entry.get("symbol") != symbol or "timestamp" not in latest_entry:
            return True

        current_ts = date_parser.isoparse(get_timestamp())
        latest_ts = date_parser.isoparse(latest_entry["timestamp"])
        age = current_ts - latest_ts
        return age > timedelta(minutes=max_age_minutes)

    except Exception as e:
        print(f"⚠️  Exception while checking update for {symbol}: {e}")
        return True

def get_symbols_to_scan(module_config):
    return [
        s for s in module_config["supported_symbols"]
        if s not in module_config["main_symbols"] and s not in module_config["blocked_symbols"]
    ]

def dict_in_list(d, lst):
    return any(d == item for item in lst)

def run_potential_trades_checker(general_config, module_config, logs_path, module_log_path, module_schema_path):

    symbols_to_process = get_symbols_to_scan(module_config)
    temporary_path = Path(logs_path) / module_config['task_config']['temp_log']

    timestamp = get_timestamp()

    print(f"🔍 Scanning {len(symbols_to_process)} symbols at {timestamp}")

    latest_entries = load_latest_entries_per_symbol(symbols_to_process, temporary_path, max_age_minutes=module_config["ohlcv_max_age_minutes"])

    for symbol in symbols_to_process:

        print(f"\n🔁 Checking symbol: {symbol}")

        entry = latest_entries.get(symbol)

        if needs_update(symbol, entry, max_age_minutes=module_config["ohlcv_max_age_minutes"]):
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

    latest_entries = load_latest_entries_per_symbol(symbols_to_process, temporary_path, max_age_minutes=module_config["ohlcv_max_age_minutes"])

    save_result = print_and_save_recommendations(latest_entries, module_config, module_log_path, module_schema_path)

    if save_result == True:
        empty_the_file(temporary_path)

if __name__ == "__main__":

    configs_and_logs = load_configs_and_logs([
        {
            "name": "symbol",
            "mid_folder": "analysis",
            "module_key": "symbol_data_fetcher",
            "extension": ".jsonl",
            "return": ["config", "logs_path", "full_log_path", "full_log_schema_path"]
        }
    ])
    general_config = configs_and_logs.get("general_config")
    symbol_config = configs_and_logs.get("symbol_config")
    symbol_logs_path = configs_and_logs.get("symbol_logs_path")
    symbol_full_log_path = configs_and_logs.get("symbol_full_log_path")
    symbol_full_log_schema_path = configs_and_logs.get("symbol_full_log_schema_path")

    run_potential_trades_checker(general_config, symbol_config, symbol_logs_path, symbol_full_log_path, symbol_full_log_schema_path)
