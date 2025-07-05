# modules/symbol_data_fetcher/tasks/top_symbols_data_fetcher.py

import json
from datetime import datetime, timedelta
from pathlib import Path
import time

from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback
from modules.symbol_data_fetcher.symbol_data_fetcher_config import (
    INTERVALS,
    SYMBOL_LOG_PATH,
    OHLCV_LOG_PATH,
    OHLCV_MAX_AGE_MINUTES,
    LOCAL_TIMEZONE,
    TOP_SYMBOL_FETCH_COOLDOWN_MINUTES,
    OHLCV_FETCH_LIMIT,
    MAX_APPEND_RETRIES,
    APPEND_RETRY_DELAY_SECONDS,
    TEMP_LOG_TOP_SYMBOLS
)

from modules.symbol_data_fetcher.utils import (
    prepare_temporary_log,
    append_temp_to_ohlcv_log_until_success,
    last_fetch_time,
)

def load_symbols_to_fetch():
    """
    Loads the most recent list of symbols to fetch from the symbol data log file.
    """
    if not SYMBOL_LOG_PATH.exists():
        print("❌ File 'symbol_data_log.jsonl' not found.")
        return []

    try:
        with open(SYMBOL_LOG_PATH, "r") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Failed to read symbol log file: {e}")
        return []

    if not lines:
        print("⚠️ File is empty.")
        return []

    try:
        last_line = lines[-1].strip()
        data = json.loads(last_line)
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON error in last line: {e}")
        return []
    except Exception as e:
        print(f"⚠️ Unexpected error reading symbol data: {e}")
        return []

    symbols = set(data.get("potential_to_long", []) + data.get("potential_to_short", []))
    return list(symbols)

def fetch_for_top_symbols():
    symbols = load_symbols_to_fetch()
    if not symbols:
        print("⚠️ No symbols to fetch.")
        return

    print(f"🔄 Fetching OHLCV data for {len(symbols)} symbols...")

    temporary_path = prepare_temporary_log(TEMP_LOG_TOP_SYMBOLS)

    for symbol in symbols:
        try:
            last_fetched = last_fetch_time(symbol)
        except Exception as e:
            print(f"⚠️ Failed to check last fetch time for {symbol}: {e}")
            continue

        if last_fetched:
            age = datetime.now(LOCAL_TIMEZONE) - last_fetched
            if age < timedelta(minutes=TOP_SYMBOL_FETCH_COOLDOWN_MINUTES):
                print(f"⏩ Skipping {symbol}, data fetched {age.total_seconds() // 60:.1f} min ago.")
                continue

        print(f"📥 Fetching: {symbol}")
        try:
            result_data, status = fetch_ohlcv_fallback(
                symbol=symbol,
                intervals=INTERVALS,
                limit=OHLCV_FETCH_LIMIT,
                log_path=temporary_path
            )
            if not status:
                print(f"⚠️ Fetch failed for {symbol}.")
        except Exception as e:
            print(f"❌ Error while fetching data for {symbol}: {e}")

    try:
        append_temp_to_ohlcv_log_until_success(
            temp_path=temporary_path,
            target_path=OHLCV_LOG_PATH,
            max_retries=MAX_APPEND_RETRIES,
            retry_delay=APPEND_RETRY_DELAY_SECONDS
        )
    except Exception as e:
        print(f"❌ Failed to append temp log to OHLCV log: {e}")

def run_top_symbols_data_fetcher():
    """
    Wrapper to run the data fetcher with timestamp logging.
    """
    print(f"🕒 Running fetch at: {datetime.now(LOCAL_TIMEZONE)}")
    fetch_for_top_symbols()


def main():
    run_top_symbols_data_fetcher()


if __name__ == "__main__":
    main()
