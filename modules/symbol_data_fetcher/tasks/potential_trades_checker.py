# modules/symbol_data_fetcher/tasks/potential_trades_checker.py

import json
from datetime import datetime, timedelta
from pathlib import Path

from modules.symbol_data_fetcher.symbol_data_fetcher_config import (
    SUPPORTED_SYMBOLS as ALL_SYMBOLS,
    MAIN_SYMBOLS,
    INTERVALS,
    OHLCV_LOG_PATH,
    SYMBOL_LOG_PATH,
    OHLCV_MAX_AGE_MINUTES,
    LOCAL_TIMEZONE
)
from modules.symbol_data_fetcher.analysis_summary import (
    analyze_all_symbols,
    save_analysis_log,
)
from modules.symbol_data_fetcher.utils import prepare_temporary_log, append_temp_to_ohlcv_log_until_success

def get_symbols_to_scan():
    return [s for s in ALL_SYMBOLS if s not in MAIN_SYMBOLS]

def last_fetch_time(symbol: str):
    if not OHLCV_LOG_PATH.exists():
        return None

    with open(OHLCV_LOG_PATH, "r") as f:
        for line in reversed(list(f)):
            try:
                entry = json.loads(line)
                if entry.get("symbol") == symbol:
                    ts_str = entry.get("timestamp")
                    if ts_str:
                        dt = datetime.fromisoformat(ts_str)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=LOCAL_TIMEZONE)
                        return dt.astimezone(LOCAL_TIMEZONE)
            except json.JSONDecodeError:
                continue
    return None

def needs_update(symbol: str, max_age_minutes: int = 180) -> bool:

    last_fetch = last_fetch_time(symbol)
    if last_fetch is None:
        return True

    now = datetime.now(LOCAL_TIMEZONE)
    age = now - last_fetch
    return age > timedelta(minutes=max_age_minutes)

def find_recent_log_entry(symbol: str):
    if not OHLCV_LOG_PATH.exists():
        return None

    today_str = datetime.now(LOCAL_TIMEZONE).date().isoformat()
    latest_entry = None
    latest_time = None

    with open(OHLCV_LOG_PATH, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)

                if entry.get("symbol") != symbol:
                    continue

                timestamp_str = entry.get("timestamp", "")
                if not timestamp_str.startswith(today_str):
                    continue

                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=LOCAL_TIMEZONE)
                timestamp = timestamp.astimezone(LOCAL_TIMEZONE)

                if latest_time is None or timestamp > latest_time:
                    latest_time = timestamp
                    latest_entry = entry

            except (json.JSONDecodeError, ValueError):
                continue

    return latest_entry

def print_and_save_recommendations():

    long_syms, short_syms, scores = analyze_all_symbols()

    if not long_syms and not short_syms:
        print("😕 No analyzable data for today.")
        return

    print("\n🧠 Verbal interpretation:")
    for sym, score in sorted(scores.items(), key=lambda x: -abs(x[1])):
        bias = "LONG" if score > 0 else "SHORT"
        print(f" - {sym}: {bias} bias (score: {score:.2f})")

    print("\n📈 💚  LONG RECOMMENDATIONS (most potential first):")
    print(" ".join(long_syms))

    print("\n📉 ❤️  SHORT RECOMMENDATIONS (most potential first):")
    print(" ".join(short_syms))

    save_analysis_log(scores)

def run_potential_trades_checker():

    import json
    from datetime import datetime, timedelta
    from pathlib import Path
    from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback

    symbols_to_process = get_symbols_to_scan()

    temporary_path = prepare_temporary_log("temporary_log_potential_trades.jsonl")

    print(f"🔍 Scanning {len(symbols_to_process)} symbols...")

    for symbol in symbols_to_process:

        print(f"\n🔁 Checking symbol: {symbol}")

        if needs_update(symbol, max_age_minutes=OHLCV_MAX_AGE_MINUTES):
            print(f"🚀 Fetching new OHLCV data: {symbol}")
            fetch_ohlcv_fallback(symbol=symbol, intervals=INTERVALS, limit=200, log_path=temporary_path)
        else:
            print(f"✅ Fresh data already exists (less than 4h old): {symbol}")

        log_entry = find_recent_log_entry(symbol)

        if log_entry:
            data_preview = log_entry.get("data_preview")
            if not data_preview:
                print("⚠️  No data_preview found, skipping analysis.")
                continue

            print(f"📂 Analysis: {symbol}")
            for interval in INTERVALS:
                analysis = data_preview.get(interval)
                if analysis:
                    print(f"📊 Interval: {interval}")
                    for key, value in analysis.items():
                        print(f"  {key.upper():<12}: {value}")
                    print()
        else:
            print(f"⚠️  No log entry found for analysis: {symbol}")
    
    # Copy values from temp log to OHLCV log
    append_temp_to_ohlcv_log_until_success(temp_path=temporary_path, target_path=OHLCV_LOG_PATH, max_retries=10, retry_delay=57)

    # Define, print, and save recommendations
    print_and_save_recommendations()

def main():
    run_potential_trades_checker()

if __name__ == "__main__":
    main()