# modules/symbol_data_fetcher/tasks/supported_symbols_data_fetcher.py

def run_supported_symbols_data_fetcher():
    
    from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback

    symbols = ["MATIC-USDT", "ADA-USDT", "XRP-USDT"]
    for symbol in symbols:
        print(f"📊 Fetching supported symbol data: {symbol}")
        # fetch_ohlcv_fallback(symbol, intervals=["1h", "4h"], limit=200)
