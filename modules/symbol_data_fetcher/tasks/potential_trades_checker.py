# modules/symbol_data_fetcher/tasks/potential_trades_checker.py

def run_potential_trades_checker():
    from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback

    symbols = ["INJ-USDT", "AVAX-USDT", "DOT-USDT"]
    for symbol in symbols:
        print(f"🔍 Checking potential traders for: {symbol}")
        # fetch_ohlcv_fallback(symbol, intervals=["1d"], limit=50