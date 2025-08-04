# integrations/price_data_fetcher/fetchers/PriceDataFetcher

# from integrations.price_data_fetcher.fetch_from_okx import fetch_from_okx
# from integrations.price_data_fetcher.fetch_from_kucoin import fetch_from_kucoin
# from integrations.price_data_fetcher.fetch_from_binance import fetch_from_binance
# from integrations.price_data_fetcher.fetch_from_bybit import fetch_from_bybit

class PriceDataFetcher:

    def __init__(self, symbol="BTCUSDT", order=None):
        self.symbol = symbol
        self.exchanges = order or CONFIG.get("exchange_priority", ["okx", "kucoin", "binance", "bybit"])

    def fetch(self):
        print("Fetch")
    #     for exchange in self.exchanges:
    #         try:
    #             method = getattr(self, f"fetch_from_{exchange}")
    #             data = method()
    #             if data:
    #                 # Tarkista että data ei ole tyhjää
    #                 price = data.get("lastPrice", 0)
    #                 volume = data.get("volume", 0)
    #                 high = data.get("highPrice", 0)
    #                 low = data.get("lowPrice", 0)

    #                 if any([price, volume, high, low]):
    #                     data['source'] = exchange
    #                     return data

    #         except Exception as e:
    #             print(f"❌ Error fetching from {exchange}: {e}")
    #             continue
    #     return None

    # def fetch_from_okx(self):
    #     return fetch_from_okx(self.symbol)

    # def fetch_from_kucoin(self):
    #     return fetch_from_kucoin(self.symbol)

    # def fetch_from_binance(self):
    #     return fetch_from_binance(self.symbol)

    # def fetch_from_bybit(self):
    #     return fetch_from_bybit(self.symbol)