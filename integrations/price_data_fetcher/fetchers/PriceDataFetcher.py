# integrations/price_data_fetcher/fetchers/price_data_fetcher.py
# version 2.0, aug 2025

from integrations.price_data_fetcher.fetchers.fetch_from_okx import fetch_from_okx
from integrations.price_data_fetcher.fetchers.fetch_from_kucoin import fetch_from_kucoin
from integrations.price_data_fetcher.fetchers.fetch_from_binance import fetch_from_binance
from integrations.price_data_fetcher.fetchers.fetch_from_bybit import fetch_from_bybit

class PriceDataFetcher:

    def __init__(self, symbol, config):
        self.config = config or {}
        self.symbol = symbol or self.config.get("settings", {}).get("symbol_to_use", "BTCUSDT")
        self.exchanges = self.config.get("settings", {}).get(
            "exchange_order", 
            ["okx", "kucoin", "binance", "bybit"]
        )

        # Dynaaminen funktiomapping – helppo muokata confista
        self.fetch_methods = {
            "okx": fetch_from_okx,
            "kucoin": fetch_from_kucoin,
            "binance": fetch_from_binance,
            "bybit": fetch_from_bybit,
        }

    def fetch(self):
        for exchange in self.exchanges:
            fetch_func = self.fetch_methods.get(exchange)
            if not fetch_func:
                print(f"⚠️ No fetch method defined for {exchange}")
                continue

            try:
                # haetaan exchangen oma config tai tyhjä
                exchange_config = self.config.get(exchange)
                if not exchange_config:  
                    # annetaan oletusconfig esim. okx:lle
                    if exchange == "okx":
                        exchange_config = {
                            "base_url": "https://www.okx.com/api/v5/market/ticker",
                            "quote_assets": ["USDT", "USDC", "BTC", "ETH", "EUR"],
                            "timeout": 5
                        }
                    else:
                        exchange_config = {}

                data = fetch_func(self.symbol, exchange_config)

                if self._is_valid_data(data):
                    data["source"] = exchange
                    return data

            except Exception as e:
                print(f"❌ Error fetching from {exchange}: {e}")
                continue
        return None

    def _is_valid_data(self, data):
        if not data or not isinstance(data, dict):
            return False

        price = data.get("lastPrice", 0)
        volume = data.get("volume", 0)
        high = data.get("highPrice", 0)
        low = data.get("lowPrice", 0)
        return any([price, volume, high, low])
