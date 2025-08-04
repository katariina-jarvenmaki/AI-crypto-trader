# integrations/price_data_fetcher/utils.py

from integrations.price_data_fetcher.fetchers.PriceDataFetcher import PriceDataFetcher

def test_single_exchange(symbol, exchange_name):
    fetcher = PriceDataFetcher(symbol=symbol, order=[exchange_name])
    data = fetcher.fetch()
    print(f"[TEST] Data from {exchange_name}:", data)