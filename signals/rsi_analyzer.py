# scripts/rsi_analyzer.py

import pandas as pd
import ta
from datetime import datetime
from scripts.signal_limiter import is_signal_allowed, update_signal_log
from integrations.binance_api_client import fetch_ohlcv_for_intervals
from configs.config import RSI_THRESHOLDS, RSI_PERIOD, DEFAULT_BUY_LIMIT, DEFAULT_SELL_LIMIT, TIMEZONE
from pytz import timezone
import pytz

INTERVALS = list(RSI_THRESHOLDS.keys())

# Calculate RSI
def calculate_rsi(close_prices, period=RSI_PERIOD):
    rsi = ta.momentum.RSIIndicator(close=close_prices, window=period)
    return rsi.rsi()

# Run RSI analyzer
def rsi_analyzer(symbol):

    data_by_interval = fetch_ohlcv_for_intervals(symbol=symbol, intervals=INTERVALS, limit=200)

    previous_rsi = None
    last_checked_rsi = None
    last_checked_interval = None

    # Go through intervals
    for interval in INTERVALS:
        df = data_by_interval.get(interval)
        thresholds = RSI_THRESHOLDS.get(interval)

        if df is None or df.empty or thresholds is None:
            continue

        rsi_series = calculate_rsi(df['close'])
        latest_rsi = rsi_series.dropna().iloc[-1]
        if isinstance(df.index, pd.DatetimeIndex):
            last_timestamp = df.index[-1]
            if last_timestamp.tzinfo is None:
                last_timestamp = last_timestamp.tz_localize('UTC')
            now = datetime.now(pytz.timezone(TIMEZONE.zone)) 
        else:
            now = datetime.now(pytz.timezone(TIMEZONE.zone)) 

        last_checked_rsi = round(latest_rsi, 2)
        last_checked_interval = interval

        buy_limit = thresholds.get("buy_limit", DEFAULT_BUY_LIMIT)
        sell_limit = thresholds.get("sell_limit", DEFAULT_SELL_LIMIT)

        if previous_rsi is not None:
            check_buy = previous_rsi <= buy_limit
            check_sell = previous_rsi >= sell_limit
        else:
            check_buy = True
            check_sell = True

        # Define values to return
        if check_buy and latest_rsi <= thresholds["buy"]:
            if is_signal_allowed(symbol, interval, "buy", now, mode="rsi"):
                return {
                    "signal": "buy",
                    "interval": interval,
                    "rsi": round(latest_rsi, 2),
                    "mode": "rsi"
                }
            else:
                continue

        elif check_sell and latest_rsi >= thresholds["sell"]:
            if is_signal_allowed(symbol, interval, "sell", now, mode="rsi"):
                return {
                    "signal": "sell",
                    "interval": interval,
                    "rsi": round(latest_rsi, 2),
                    "mode": "rsi"
                }
            else:
                continue

        previous_rsi = latest_rsi

    return {
        "signal": "none",
        "interval": last_checked_interval,
        "rsi": last_checked_rsi,
        "mode": "rsi"
    }
