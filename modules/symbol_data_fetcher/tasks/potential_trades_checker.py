# modules/symbol_data_fetcher/tasks/potential_trades_checker.py

import json
from datetime import datetime, timedelta

from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback
from modules.symbol_data_fetcher.config_symbol_data_fetcher import (
    MAIN_SYMBOLS,
    INTERVALS,
    OHLCV_LOG_PATH,
    LOCAL_TIMEZONE,
    OHLCV_FETCH_LIMIT,
    MAX_APPEND_RETRIES,
    TASK_CONFIG,
    SUPPORTED_SYMBOLS as ALL_SYMBOLS
)
from modules.symbol_data_fetcher.analysis_summary import analyze_all_symbols
from modules.symbol_data_fetcher.utils import (
    prepare_temporary_log,
    append_temp_to_ohlcv_log_until_success,
    last_fetch_time,
)

# Use configuration according to the "potential" task
CONFIG = TASK_CONFIG["potential"]
MAX_AGE_MINUTES = CONFIG.get("cooldown_minutes", 3) * 60
RETRY_DELAY = CONFIG.get("retry_delay", 60)
TEMP_LOG_PATH = CONFIG.get("temp_log", "temporary_log_potential.jsonl")

def get_symbols_to_scan():
    return [s for s in ALL_SYMBOLS if s not in MAIN_SYMBOLS]

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

def needs_update(symbol: str, max_age_minutes: int = MAX_AGE_MINUTES) -> bool:
    last_fetch = last_fetch_time(symbol)
    if last_fetch is None:
        return True

    now = datetime.now(LOCAL_TIMEZONE)
    age = now - last_fetch
    return age > timedelta(minutes=max_age_minutes)

def print_and_save_recommendations():
    long_syms, short_syms, scores = analyze_all_symbols()

    if not long_syms and not short_syms:
        print("😕 No analyzable data for today.")
        return

    print("\n🧠 Verbal interpretation:")
    for sym, data in sorted(scores.items(), key=lambda x: -abs(x[1]["score"])):
        score = data["score"]
        bias = "LONG" if score > 0 else "SHORT"
        print(f" - {sym}: {bias} bias (score: {score:.2f})")

    print("\n📈 💚  LONG RECOMMENDATIONS (most potential first):")
    print(" ".join(long_syms))

    print("\n📉 ❤️  SHORT RECOMMENDATIONS (most potential first):")
    print(" ".join(short_syms))

    # Save analysis log if implemented elsewhere
    from modules.symbol_data_fetcher.analysis_summary import save_analysis_log
    save_analysis_log(scores)

def run_potential_trades_checker():
    symbols_to_process = get_symbols_to_scan()
    temporary_path = prepare_temporary_log(TEMP_LOG_PATH)

    print(f"🔍 Scanning {len(symbols_to_process)} symbols...")

    for symbol in symbols_to_process:
        print(f"\n🔁 Checking symbol: {symbol}")

        if needs_update(symbol):
            print(f"🚀 Fetching new OHLCV data: {symbol}")
            fetch_ohlcv_fallback(
                symbol=symbol,
                intervals=INTERVALS,
                limit=OHLCV_FETCH_LIMIT,
                log_path=temporary_path
            )
        else:
            hours = MAX_AGE_MINUTES // 60
            minutes = MAX_AGE_MINUTES % 60
            age_str = f"{hours}h {minutes}min" if hours else f"{minutes}min"
            print(f"✅ Fresh data already exists (less than {age_str} old): {symbol}")

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

    append_temp_to_ohlcv_log_until_success(
        temp_path=temporary_path,
        target_path=OHLCV_LOG_PATH,
        max_retries=MAX_APPEND_RETRIES,
        retry_delay=RETRY_DELAY
    )

    print_and_save_recommendations()

def main():
    run_potential_trades_checker()

if __name__ == "__main__":
    main()
