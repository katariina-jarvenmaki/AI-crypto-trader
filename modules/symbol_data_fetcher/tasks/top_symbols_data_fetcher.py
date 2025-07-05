# modules/symbol_data_fetcher/tasks/top_symbols_data_fetcher.py
# Lisää tarkistus ettei haeta uutta jos OHLCV:ssä on jo alle 5 min vanha kirjaus
# Lisää tähän temp tiedosto tallennut > OHLCV tallennus
# Pidä huoli että tämä löytää uusimmat päivämäärän mukaan uusimmat tiedot eikä kato vain vikaa riviä
# Testaa että cron ajo toimii 

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

def fetch_for_top_symbols():

    symbols = load_symbols_to_fetch()
    if not symbols:
        print("⚠️ Ei symboleita haettavaksi.")
        return

    print(f"🔄 Haetaan OHLCV-tiedot {len(symbols)} kolikolle...")

    for symbol in symbols:

        print(f"📥 Haetaan: {symbol}")
        result_data, status = fetch_ohlcv_fallback(symbol=symbol, intervals=INTERVALS, limit=200)

def run_top_symbols_data_fetcher():

    print(f"🕒 Haku käynnissä: {datetime.now(LOCAL_TIMEZONE)}")
    fetch_for_top_symbols()
    
def main():

    run_top_symbols_data_fetcher()

if __name__ == "__main__":
    main()
