# modules/symbol_data_fetcher/tasks/main_symbols_data_fetcher.py

def run_main_symbols_data_fetcher():

    from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback

    symbols = ["BTC-USDT", "ETH-USDT", "SOL-USDT"]  # tai lue konfigista
    for symbol in symbols:
        print(f"🔁 Fetching data for {symbol}")
        # fetch_ohlcv_fallback(symbol, intervals=["5m", "15m", "1h"], limit=100)
