# integrations/price_data_fetcher/price_data_fetcher.py

import json
from typing import List

from integrations.price_data_fetcher.config_price_data_fetcher import CONFIG
from integrations.price_data_fetcher.price_data_from_okx import fetch_from_okx
from integrations.price_data_fetcher.price_data_from_kucoin import fetch_from_kucoin
from integrations.price_data_fetcher.price_data_from_binance import fetch_from_binance
from integrations.price_data_fetcher.price_data_from_bybit import fetch_from_bybit

class PriceDataFetcher:
    def __init__(self, symbol="BTCUSDT", order=None):
        self.symbol = symbol
        self.exchanges = order or CONFIG.get("exchange_priority", ["okx", "kucoin", "binance", "bybit"])

        print(f"Fetching symbol data for symbol {self.symbol}")
        print(f"Exchange priority {self.exchanges}")

    def fetch(self):
        for exchange in self.exchanges:
            try:
                method = getattr(self, f"fetch_from_{exchange}")
                data = method()
                if data:
                    data['source'] = exchange
                    return data
            except Exception as e:
                print(f"Error fetching from {exchange}: {e}")
                continue
        return None

    # WRAPPER-METODIT
    def fetch_from_okx(self):
        return fetch_from_okx(self.symbol)

    def fetch_from_kucoin(self):
        return fetch_from_kucoin(self.symbol)

    def fetch_from_binance(self):
        return fetch_from_binance(self.symbol)

    def fetch_from_bybit(self):
        return fetch_from_bybit(self.symbol)

def get_latest_symbols_from_log(file_path: str) -> List[str]:

    with open(file_path, "r") as f:
        lines = f.readlines()
        if not lines:
            return []
        last_entry = json.loads(lines[-1])

        combined_symbols = set()
        for key in CONFIG["symbol_keys"]:
            combined_symbols.update(last_entry.get(key, []))

        return list(combined_symbols)

def test_single_exchange(symbol, exchange_name):
    fetcher = PriceDataFetcher(symbol=symbol, order=[exchange_name])
    data = fetcher.fetch()
    print(f"[TEST] Data from {exchange_name}:", data)

def main():

    print("Running a price data fetcher...")

    symbols = get_latest_symbols_from_log(CONFIG["symbol_log_path"])

    if not symbols:
       print("No symbols found in latest symbol log.")
       return
    print(f"Found {len(symbols)} symbols to process...")

    for i, symbol in enumerate(symbols):

        fetcher = PriceDataFetcher(symbol=symbol)
        data = fetcher.fetch()
        print(data)
        
if __name__ == "__main__":

    main()
    # test_single_exchange("BTCUSDT", "okx")
    # test_single_exchange("BTCUSDT", "kucoin")
    # test_single_exchange("BTCUSDT", "binance")
    # test_single_exchange("BTCUSDT", "bybit")