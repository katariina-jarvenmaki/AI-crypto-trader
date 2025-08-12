# integrations/price_data_fetcher/fetchers/price_data_fetcher.py
# version 2.0, aug 2025

from integrations.price_data_fetcher.fetchers.fetch_from_okx import fetch_from_okx
from integrations.price_data_fetcher.fetchers.fetch_from_kucoin import fetch_from_kucoin
from integrations.price_data_fetcher.fetchers.fetch_from_binance import fetch_from_binance
from integrations.price_data_fetcher.fetchers.fetch_from_bybit import fetch_from_bybit

class PriceDataFetcher:

    def __init__(self, symbol=None, config=None, order=None):

        if config is None:
            raise ValueError("⚠️ PriceDataFetcher requires a 'config' parameter.")

        self.config = config
        settings = config.get("settings", {})
        self.symbol = symbol if symbol else settings.get("symbol_to_use")
        self.exchanges = order if order else settings.get("exchange_order")

    def fetch(self):

        for exchange in self.exchanges:

            try:
                method = getattr(self, f"fetch_from_{exchange}")
                data = method()

                if data:
                    price = data.get("lastPrice", 0)
                    volume = data.get("volume", 0)
                    high = data.get("highPrice", 0)
                    low = data.get("lowPrice", 0)

                    if any([price, volume, high, low]):
                        data['source'] = exchange
                        return data

            except Exception as e:
                print(f"❌ Error fetching from {exchange}: {e}")
                continue

        return None

    def fetch_from_okx(self):
        return fetch_from_okx(self.symbol, self.config)

    def fetch_from_kucoin(self):
        return fetch_from_kucoin(self.symbol, self.config)

    def fetch_from_binance(self):
        return fetch_from_binance(self.symbol, self.config)

    def fetch_from_bybit(self):
        return fetch_from_bybit(self.symbol, self.config)