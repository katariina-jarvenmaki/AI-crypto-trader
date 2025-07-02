# Run 1: Use the fetch_ohlcv_fallback function normally

data, exchange = fetch_ohlcv_fallback("BTC/USDT", intervals=["1m", "5m"], start_time="2024-01-01", end_time="2024-01-02")

# Latest fetch from the log

re_fetch_from_log(log_index=-1)
