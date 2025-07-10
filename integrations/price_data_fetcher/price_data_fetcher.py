# integrations/price_data_fetcher/price_data_fetcher.py

from integrations.price_data_fetcher.config_price_data_fetcher import CONFIG
from integrations.price_data_fetcher.price_data_from_okx import fetch_from_okx
from integrations.price_data_fetcher.price_data_from_kucoin import fetch_from_kucoin
from integrations.price_data_fetcher.price_data_from_binance import fetch_from_binance
from integrations.price_data_fetcher.price_data_from_bybit import fetch_from_bybit
from integrations.price_data_fetcher.utils import ensure_log_file_exists, append_to_log, trim_log_file, get_latest_symbols_from_log, test_single_exchange

class PriceDataFetcher:

    def __init__(self, symbol="BTCUSDT", order=None):
        self.symbol = symbol
        self.exchanges = order or CONFIG.get("exchange_priority", ["okx", "kucoin", "binance", "bybit"])

    def fetch(self):
        for exchange in self.exchanges:
            try:
                method = getattr(self, f"fetch_from_{exchange}")
                data = method()
                if data:
                    # Tarkista että data ei ole tyhjää
                    price = data.get("lastPrice", 0)
                    volume = data.get("volume", 0)
                    high = data.get("highPrice", 0)
                    low = data.get("lowPrice", 0)

                    if any([price, volume, high, low]):
                        data['source'] = exchange
                        return data
                    else:
                        # print(f"⚠️  {self.symbol} from {exchange} has empty or zero data, trying next exchange...")
            except Exception as e:
                print(f"❌ Error fetching from {exchange}: {e}")
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

def main():

    print("Running a price data fetcher...")

    log_path = CONFIG["price_data_log_path"]
    ensure_log_file_exists(log_path)

    symbols = get_latest_symbols_from_log(CONFIG["symbol_log_path"])

    if not symbols:
        print("No symbols found in latest symbol log.")
        return
    print(f"Found {len(symbols)} symbols to process...")

    for symbol in symbols:
        fetcher = PriceDataFetcher(symbol=symbol)
        data = fetcher.fetch()
        # print(data)

        if data:
            append_to_log(log_path, symbol, data.get("source"), data)

    trim_log_file(log_path, CONFIG.get("max_log_lines", 10000))

if __name__ == "__main__":

    main()
    # test_single_exchange("BTCUSDT", "okx")
    # test_single_exchange("BTCUSDT", "kucoin")
    # test_single_exchange("BTCUSDT", "binance")
    # test_single_exchange("BTCUSDT", "bybit")