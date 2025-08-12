# integrations/price_data_fetcher/price_data_fetcher.py
# version 2.0, aug 2025

from datetime import datetime, timezone, timedelta
from utils.get_symbols_to_use import get_symbols_to_use
from modules.save_and_validate.save_and_validate import save_and_validate
from integrations.price_data_fetcher.fetchers.PriceDataFetcher import PriceDataFetcher
from integrations.price_data_fetcher.utils import test_single_exchange, config_and_log_loader

def price_data_fetcher():

    print("\nRunning a Price Data Fetcher...\n")

    module_log_path, module_log_schema_path, module_config, symbol_config, symbol_log_path = config_and_log_loader()
    result = get_symbols_to_use(symbol_config, symbol_log_path, None)
    all_symbols = result["all_symbols"]

    if not all_symbols:
        print("\nNo symbols found in latest symbol log.\n")
        return
    print(f"\nFound {len(all_symbols)} symbols to process...\n")

    tz_offset = timezone(timedelta(hours=3))  # +03:00
    entries = []

    print("Getting results for symbols:\n")

    for symbol in all_symbols:

        fetcher = PriceDataFetcher(symbol=symbol, config=module_config)
        raw_data = fetcher.fetch()

        if not raw_data:
            print(f"⚠️ No data for {symbol}")
            continue

        entry = {
            "timestamp": datetime.now(tz_offset).isoformat(),
            "source_exchange": raw_data.get("source", "").capitalize(),
            "symbol": symbol,
            "last_price": raw_data.get("lastPrice"),
            "price_change_percent": raw_data.get("priceChangePercent"),
            "high_price": raw_data.get("highPrice"),
            "low_price": raw_data.get("lowPrice"),
            "volume": raw_data.get("volume"),
            "turnover": raw_data.get("turnover")
        }
        print(entry)
        entries.append(entry)

    if entries:
        save_and_validate(
            data=entries,
            path=module_log_path,
            schema=module_log_schema_path,
            verbose=False
        )
        print(f"\n✅ Logged {len(entries)} price data entries to {module_log_path}\n")

if __name__ == "__main__":

    price_data_fetcher()

    # test_single_exchange("BTCUSDT", "okx")
    # test_single_exchange("BTCUSDT", "kucoin")
    # test_single_exchange("BTCUSDT", "binance")
    # test_single_exchange("BTCUSDT", "bybit")
