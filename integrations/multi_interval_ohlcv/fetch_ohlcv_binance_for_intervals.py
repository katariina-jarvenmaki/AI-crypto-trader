# integrations/multi_interval_ohlcv/fetch_ohlcv_binance_for_intervals.py

import pandas as pd
import time
from binance.exceptions import BinanceAPIException
from requests.exceptions import ReadTimeout
from configs.config import DEFAULT_INTERVALS, DEFAULT_OHLCV_LIMIT
from integrations.binance_api_client import client

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

def fetch_ohlcv_binance(symbol, intervals=None, limit=None, start_time=None, end_time=None):
    intervals = intervals or DEFAULT_INTERVALS
    limit = limit or DEFAULT_OHLCV_LIMIT
    result = {}

    for interval in intervals:
        success = False
        for _ in range(MAX_RETRIES):
            try:
                params = {
                    "symbol": symbol,
                    "interval": interval,
                    "limit": limit
                }

                if start_time:
                    params["startTime"] = int(start_time.timestamp() * 1000)
                if end_time:
                    params["endTime"] = int(end_time.timestamp() * 1000)

                klines = client.get_klines(**params)

                df = pd.DataFrame(klines, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_asset_volume', 'number_of_trades',
                    'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
                ])
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                df = df.astype(float)
                result[interval] = df.sort_index()
                success = True
                break

            except (BinanceAPIException, ReadTimeout):
                time.sleep(RETRY_DELAY)

        if not success:
            raise Exception(f"Binance fetch failed for {symbol} ({interval})")

    return result, "Binance"


