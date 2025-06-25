# integrations/multi_interval_ohlcv/fetch_ohlcv_kucoin_for_intervals.py

import requests
import pandas as pd
from configs.config import DEFAULT_INTERVALS, DEFAULT_OHLCV_LIMIT

def fetch_ohlcv_kucoin(symbol, intervals=None, limit=None, start_time=None, end_time=None):
    intervals = intervals or DEFAULT_INTERVALS
    limit = limit or DEFAULT_OHLCV_LIMIT
    interval_map = {
        '1m': '1min', '3m': '3min', '5m': '5min', '15m': '15min',
        '30m': '30min', '1h': '1hour', '2h': '2hour', '4h': '4hour',
        '1d': '1day', '1w': '1week'
    }

    symbol = symbol.replace("USDT", "-USDT")
    base_url = "https://api.kucoin.com/api/v1/market/candles"
    result = {}

    for interval in intervals:
        try:
            mapped = interval_map[interval]
            params = {
                "type": mapped,
                "symbol": symbol
            }

            if start_time:
                params["startAt"] = int(start_time.timestamp())
            if end_time:
                params["endAt"] = int(end_time.timestamp())

            r = requests.get(base_url, params=params).json()
            rows = r['data']

            df = pd.DataFrame(rows, columns=[
                'timestamp', 'open', 'close', 'high', 'low', 'volume', 'turnover'
            ])
            df['timestamp'] = pd.to_datetime(pd.to_numeric(df['timestamp']), unit='s')
            df.set_index('timestamp', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

            result[interval] = df.sort_index()

        except Exception:
            result[interval] = pd.DataFrame()

    return result, "Kucoin"

