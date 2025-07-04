# modules/symbol_data_fetcher/tasks/potential_trades_checker.py

import json
from datetime import datetime, timedelta
from pathlib import Path

from modules.symbol_data_fetcher.supported_symbol_config import (
    SUPPORTED_SYMBOLS as ALL_SYMBOLS,
    MAIN_SYMBOLS,
    INTERVALS,
    OHLCV_LOG_PATH,
    SYMBOL_LOG_PATH,
)
from modules.symbol_data_fetcher.analysis_summary import (
    analyze_all_symbols,
    save_analysis_log,
)

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
                        return datetime.fromisoformat(ts_str)
            except json.JSONDecodeError:
                continue
    return None

def needs_update(symbol: str, max_age_minutes: int = 240) -> bool:
    last_fetch = last_fetch_time(symbol)
    if last_fetch is None:
        return True

    now = datetime.utcnow()
    age = now - last_fetch
    return age > timedelta(minutes=max_age_minutes)

def find_recent_log_entry(symbol: str):

    if not OHLCV_LOG_PATH.exists():
        return None

    today_str = datetime.utcnow().date().isoformat()
    with open(OHLCV_LOG_PATH, "r") as f:
        for line in reversed(list(f)):
            try:
                entry = json.loads(line)
                if entry.get("symbol") == symbol and entry.get("timestamp", "").startswith(today_str):
                    return entry
            except json.JSONDecodeError:
                continue
    return None

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

    print(f"🔍 Scanning {len(symbols_to_process)} symbols...")

    for symbol in symbols_to_process:
        print(f"\n🔁 Checking symbol: {symbol}")

        if needs_update(symbol):
            print(f"🚀 Fetching new OHLCV data: {symbol}")
            fetch_ohlcv_fallback(symbol=symbol, intervals=INTERVALS, limit=200)
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
        
    print_and_save_recommendations()

def main():

    run_potential_trades_checker()

if __name__ == "__main__":
    main()