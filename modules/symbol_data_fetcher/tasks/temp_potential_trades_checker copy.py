
from pathlib import Path
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from utils.get_timestamp import get_timestamp 
from modules.pathbuilder.pathbuilder import pathbuilder
from utils.load_latest_log_entries import load_latest_log_entries
from modules.load_and_validate.load_and_validate import load_and_validate 
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback

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
        print(f"⚠️ Error while checking update need for {symbol}: {e}")
        return True

def get_latest_entry(symbol, file_path, max_age_minutes=60):
    try:
        end_time = get_timestamp()
        start_time = (date_parser.isoparse(end_time) - timedelta(minutes=max_age_minutes)).isoformat()

        entries = load_latest_log_entries(
            file_path=file_path,
            limit=1,
            use_timestamp=True,
            symbols=[symbol],
            start_time=start_time,
            end_time=end_time,
        )

        if not entries:
            return {}

        return entries[0]  # 🔁 Palautetaan koko tietue

    except Exception as e:
        print(f"Error in get_latest_entry: {e}")
        return {}

def get_symbols_to_scan():
    return [
        s for s in module_config["supported_symbols"]
        if s not in module_config["main_symbols"] and s not in module_config["blocked_symbols"]
    ]

def run_potential_trades_checker(general_config, module_config, ohlcv_log_path):

    symbols_to_process = get_symbols_to_scan()
    paths = pathbuilder(extension=".jsonl", file_name=general_config["module_filenames"]["potential_trades_checker"], mid_folder="analysis")
    temporary_path = paths["full_temp_log_path"]
    schema_path = paths["full_log_schema_path"]
    timestamp = get_timestamp()

    print(f"🔍 Scanning {len(symbols_to_process)} symbols at {timestamp}")

    for symbol in symbols_to_process:
        print(f"\n🔁 Checking symbol: {symbol}")

        latest_ohlcv_entries = get_latest_entry(symbol, ohlcv_log_path, max_age_minutes=module_config["ohlcv_max_age_minutes"])

        if needs_update(symbol, latest_ohlcv_entries, max_age_minutes=module_config["ohlcv_max_age_minutes"]):
            print(f"🚀 Fetching new OHLCV data: {symbol}")
            fetch_ohlcv_fallback(
                symbol=symbol,
                intervals=module_config["intervals"],
                limit=module_config["ohlcv_fetch_limit"],
                log_path=temporary_path
            )
        else:
            hours = module_config["ohlcv_max_age_minutes"] // 60
            minutes = module_config["ohlcv_max_age_minutes"] % 60
            age_str = f"{hours}h {minutes}min" if hours else f"{minutes}min"
            print(f"✅ Fresh data already exists (less than {age_str} old): {symbol}")

        if latest_ohlcv_entries:
            data_preview = latest_ohlcv_entries.get("data_preview")
            if not data_preview:
                print("⚠️  No data_preview found, skipping analysis.")
                continue
            for interval in module_config["intervals"]:
                analysis = data_preview.get(interval)
                if analysis:
                    print(f"📊 Interval: {interval}")
                    for key, value in analysis.items():
                        print(f"  {key.upper():<12}: {value}")
                    print()
        else:
            print(f"⚠️  No log entry found for analysis: {symbol}")

        # print(f"temporary_path: {temporary_path}")
        # print(f"ohlcv_log_path: {ohlcv_log_path}")
        # print(f"retry_delay: {module_config['potential']['symbol_keys']}")
        # print(f"retry_delay: {module_config['potential']['cooldown_minutes']}")
        # print(f"retry_delay: {module_config['potential']['retry_delay']}")
        # print(f"retry_delay: {module_config['potential']['temp_log']}")
        # print(f"max_append_retries: {module_config['max_append_retries']}")

if __name__ == "__main__":

    general_config = load_and_validate()
    paths = pathbuilder(extension=".json", file_name=general_config["module_filenames"]["symbol_data_fetcher"], mid_folder="analysis")

    module_config = load_and_validate(file_path=paths["full_config_path"], schema_path=paths["full_config_schema_path"])

    log_paths = pathbuilder(extension=".jsonl", file_name=general_config["module_filenames"]["multi_interval_ohlcv"], mid_folder="fetch")
    ohlcv_log_path = Path(log_paths["full_log_path"])

    run_potential_trades_checker(general_config, module_config, ohlcv_log_path)
