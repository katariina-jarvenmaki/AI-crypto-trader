# scripts/market_scanner_top_symbols.py

import json
from pathlib import Path
from datetime import datetime
from time import sleep

import schedule  # asenna tarvittaessa: pip install schedule

from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback, save_fetch_log_with_data
from configs.market_scanner_config import INTERVALS, LOG_PATH, MARKET_SCANNER_LOG_PATH

def load_symbols_to_fetch():

    if not MARKET_SCANNER_LOG_PATH.exists():
        print("❌ Analyysilokia ei löytynyt.")
        return []

    with open(MARKET_SCANNER_LOG_PATH, "r") as f:
        lines = f.readlines()

    if not lines:
        print("⚠️ Lokitiedosto on tyhjä.")
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
        print("⚠️  Ei symboleita haettavaksi.")
        return

    print(f"🔄 Haetaan OHLCV-tiedot {len(symbols)} kolikolle...")

    for symbol in symbols:
        print(f"📥 Haetaan: {symbol}")
        result_data, status = fetch_ohlcv_fallback(symbol=symbol, intervals=INTERVALS, limit=200)
        # Voit lisätä tallennuksen tai muuta käsittelyä tähän tarvittaessa

def job():
    print(f"🕒 Ajastettu haku käynnissä: {datetime.utcnow().isoformat()} UTC")
    fetch_for_top_symbols()

if __name__ == "__main__":
    # Suoritetaan heti kerran aluksi
    job()

    # Ajetaan job joka 30. minuutti
    schedule.every(30).minutes.do(job)

    while True:
        schedule.run_pending()
        sleep(1)
