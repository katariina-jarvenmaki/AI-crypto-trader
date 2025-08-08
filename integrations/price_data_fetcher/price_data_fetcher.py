# integrations/price_data_fetcher/price_data_fetcher.py

from utils.get_symbols_to_use import get_symbols_to_use
from modules.save_and_validate.save_and_validate import save_and_validate
from integrations.price_data_fetcher.fetchers.PriceDataFetcher import PriceDataFetcher
from integrations.price_data_fetcher.utils import test_single_exchange, config_and_log_loader

def price_data_fetcher():

    print("\nRunning a Price Data Fetcher...\n")

    module_log_path, module_log_schema_path, module_config, symbol_config, symbol_log_path = config_and_log_loader()
    result = get_symbols_to_use(symbol_config, symbol_log_path, None)
    all_symbols = result["all_symbols"]
    message = result["message"]

    if not all_symbols:
        print("\nNo symbols found in latest symbol log.\n")
        return
    print(f"\nFound {len(all_symbols)} symbols to process...\n")

    print("Getting results for symbols:\n")
    for symbol in all_symbols:
        fetcher = PriceDataFetcher(symbol=symbol, config=module_config)
        to_save = fetcher.fetch()
        print(to_save)

    if to_save:
        save_and_validate(
            data=to_save,
            path=module_log_path,
            schema=module_log_schema_path,
            verbose=False
        )
        ts = to_save.get("timestamp", "unknown_time")
        print(f"✅ Logged price data for {symbol} at {ts}")

if __name__ == "__main__":

    price_data_fetcher()
    # test_single_exchange("BTCUSDT", "okx")
    # test_single_exchange("BTCUSDT", "kucoin")
    # test_single_exchange("BTCUSDT", "binance")
    # test_single_exchange("BTCUSDT", "bybit")