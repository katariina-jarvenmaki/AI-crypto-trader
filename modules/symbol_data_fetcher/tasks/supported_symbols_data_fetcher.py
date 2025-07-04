# modules/symbol_data_fetcher/tasks/supported_symbols_data_fetcher.py

def run_supported_symbols_data_fetcher():

    import json
    from datetime import datetime, timedelta
    from pathlib import Path
    from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback
    from modules.symbol_data_fetcher.symbol_data_fetcher_config import (
        INTERVALS,
        SYMBOL_LOG_PATH,
        OHLCV_LOG_PATH,
        OHLCV_MAX_AGE_MINUTES,
        LOCAL_TIMEZONE
    )
    
    def load_symbols_to_fetch():

        if not SYMBOL_LOG_PATH.exists():
            print("❌ symbol_data_log.jsonl ei löytynyt.")
            return []

        with open(SYMBOL_LOG_PATH, "r") as f:
            lines = f.readlines()

        if not lines:
            print("⚠️ Tiedosto on tyhjä.")
            return []

        try:
            last_line = lines[-1].strip()
            data = json.loads(last_line)

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON-virhe viimeisessä rivissä: {e}")
            return []

        symbols = set(data.get("potential_to_long", []) + data.get("potential_to_short", []))
        return list(symbols)

    def has_recent_ohlcv_log_entry(symbol: str, max_age_minutes: int = 5) -> bool:

        if not OHLCV_LOG_PATH.exists():
            return False

        now = datetime.now(LOCAL_TIMEZONE)

        try:
            with open(OHLCV_LOG_PATH, "r") as f:
                for line in reversed(list(f)):
                    try:
                        entry = json.loads(line)
                        if entry.get("symbol") == symbol:
                            ts_str = entry.get("timestamp")
                            if ts_str:
                                entry_time = datetime.fromisoformat(ts_str).astimezone(LOCAL_TIMEZONE)
                                age = now - entry_time
                                return age <= timedelta(minutes=max_age_minutes)
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"⚠️ Virhe tarkistettaessa logia: {e}")

        return False

    def fetch_for_top_symbols():
        symbols = load_symbols_to_fetch()
        if not symbols:
            print("⚠️ Ei symboleita haettavaksi.")
            return

        print(f"🔄 Haetaan OHLCV-tiedot {len(symbols)} kolikolle...")

        for symbol in symbols:
            if has_recent_ohlcv_log_entry(symbol):
                print(f"⏩ Skipataan {symbol} (tuore kirjaus löytyy)")
                continue

            print(f"📥 Haetaan: {symbol}")
            result_data, status = fetch_ohlcv_fallback(symbol=symbol, intervals=INTERVALS, limit=200)

    print(f"🕒 Haku käynnissä: {datetime.now(LOCAL_TIMEZONE)}")
    fetch_for_top_symbols()

def main():
    run_supported_symbols_data_fetcher()

if __name__ == "__main__":
    main()


