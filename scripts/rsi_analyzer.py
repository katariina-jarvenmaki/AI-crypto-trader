# scripts/rsi_analyzer.py
import pandas as pd
import ta
from datetime import datetime
from scripts.signal_limiter import is_signal_allowed, update_signal_log
from scripts.binance_api_client import fetch_ohlcv_for_intervals
from configs.config import RSI_THRESHOLDS

INTERVALS = list(RSI_THRESHOLDS.keys())

def calculate_rsi(close_prices, period=14):
    rsi = ta.momentum.RSIIndicator(close=close_prices, window=period)
    return rsi.rsi()

def rsi_analyzer(symbol):
    data_by_interval = fetch_ohlcv_for_intervals(symbol=symbol, intervals=INTERVALS, limit=200)

    previous_rsi = None
    last_checked_rsi = None
    last_checked_interval = None

    for interval in INTERVALS:
        df = data_by_interval.get(interval)
        thresholds = RSI_THRESHOLDS.get(interval)

        if df is None or df.empty or thresholds is None:
            continue

        rsi_series = calculate_rsi(df['close'])
        latest_rsi = rsi_series.dropna().iloc[-1]
        now = df.index[-1] if isinstance(df.index, pd.DatetimeIndex) else pd.to_datetime(df['timestamp'].iloc[-1])

        last_checked_rsi = round(latest_rsi, 2)
        last_checked_interval = interval

        if previous_rsi is not None:
            check_buy = previous_rsi <= thresholds.get("buy_limit", float("inf"))
            check_sell = previous_rsi >= thresholds.get("sell_limit", float("-inf"))
        else:
            check_buy = True
            check_sell = True

        if check_buy and latest_rsi <= thresholds["buy"]:
            # Lisätty strategy="rsi"
            if is_signal_allowed(symbol, interval, "buy", now, strategy="rsi"):
                update_signal_log(symbol, interval, "buy", now, strategy="rsi")
                return {
                    "signal": "buy",
                    "interval": interval,
                    "rsi": round(latest_rsi, 2),
                    "strategy": "rsi"
                }

        elif check_sell and latest_rsi >= thresholds["sell"]:
            # Lisätty strategy="rsi"
            if is_signal_allowed(symbol, interval, "sell", now, strategy="rsi"):
                update_signal_log(symbol, interval, "sell", now, strategy="rsi")
                return {
                    "signal": "sell",
                    "interval": interval,
                    "rsi": round(latest_rsi, 2),
                    "strategy": "rsi"
                }

        previous_rsi = latest_rsi

    return {
        "signal": "none",
        "interval": last_checked_interval,
        "rsi": last_checked_rsi,
        "strategy": "rsi"
    }
