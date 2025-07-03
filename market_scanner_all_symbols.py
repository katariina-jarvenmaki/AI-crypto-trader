# market_scanner.py
import json
from datetime import datetime, timedelta
from pathlib import Path

from configs.market_scanner_config import SUPPORTED_SYMBOLS, INTERVALS, LOG_PATH, MARKET_SCANNER_LOG_PATH 
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback
from scripts.market_scanner_analysis_summary import analyze_all_symbols, save_analysis_log

def has_fetched_today(symbol: str) -> bool:

    if not LOG_PATH.exists():
        return False

    today_str = datetime.utcnow().date().isoformat()

    with open(LOG_PATH, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                entry_date = entry.get("timestamp", "")[:10]
                if entry.get("symbol") == symbol and entry_date == today_str:
                    return True
            except json.JSONDecodeError:
                continue
    return False

def find_today_log_entry(symbol: str):

    if not LOG_PATH.exists():
        return None

    today_str = datetime.utcnow().date().isoformat()
    latest_entry = None

    with open(LOG_PATH, "r") as f:
        for line in reversed(list(f)):
            try:
                entry = json.loads(line)
                if entry.get("symbol") == symbol and entry.get("timestamp", "").startswith(today_str):
                    latest_entry = entry
                    break
            except json.JSONDecodeError:
                continue

    return latest_entry

def print_recommendations():
    long_syms, short_syms, scores = analyze_all_symbols()

    if not long_syms and not short_syms:
        print("😕 Ei analysoitavaa dataa tältä päivältä.")
        return

    print("\n🧠 Sanallinen tulkinta:")
    for sym, score in sorted(scores.items(), key=lambda x: -abs(x[1])):
        bias = "LONG" if score > 0 else "SHORT"
        print(f" - {sym}: {bias}-bias (score: {score:.2f})")

    print("\n📈💚 LONG-SUOSITUKSET (eniten potentiaalia ensin):")
    print(" ".join(long_syms))

    print("\n📉❤️ SHORT-SUOSITUKSET (eniten potentiaalia ensin):")
    print(" ".join(short_syms))

    save_analysis_log(scores)

def main():
    
    print("🔍 Starting symbol loop...")

    for symbol in SUPPORTED_SYMBOLS:
        print(f"\n🔁 Checking log for symbol: {symbol}")

        log_entry = find_today_log_entry(symbol)

        if log_entry:
            print(f"📂 Using existing log entry for {symbol} from {log_entry['timestamp']}")

            data_preview = log_entry.get("data_preview")
            if not data_preview:
                print("⚠️  No data_preview found, skipping analysis.")
                continue

            # Use existing data_preview and simulate analysis display
            for interval in INTERVALS:
                analysis = data_preview.get(interval)
                if not analysis:
                    continue

                print(f"📊 Interval: {interval}")
                for key, value in analysis.items():
                    print(f"  {key.upper():<12}: {value}")
                print()

            continue

        print(f"🚀 Fetching OHLCV data for {symbol}")
        fetch_ohlcv_fallback(symbol=symbol, intervals=INTERVALS, limit=200)

if __name__ == "__main__":
    main()
    print_recommendations()