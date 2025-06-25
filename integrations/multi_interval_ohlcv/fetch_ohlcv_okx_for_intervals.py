# integrations/multi_interval_ohlcv/fetch_ohlcv_okx_for_intervals.py

import requests
import pandas as pd
from configs.config import DEFAULT_INTERVALS, DEFAULT_OHLCV_LIMIT

def fetch_ohlcv_okx(symbol, intervals=None, limit=None, start_time=None, end_time=None):
    intervals = intervals or DEFAULT_INTERVALS
    limit = limit or DEFAULT_OHLCV_LIMIT
    interval_map = {
        '1m': '1m', '3m': '3m', '5m': '5m', '15m': '15m',
        '30m': '30m', '1h': '1H', '2h': '2H', '4h': '4H',
        '1d': '1D', '1w': '1W'
    }

    symbol = symbol.replace("USDT", "-USDT")
    base_url = "https://www.okx.com/api/v5/market/candles"
    result = {}

    for interval in intervals:
        try:
            mapped = interval_map[interval]
            params = {
                "instId": symbol,
                "bar": mapped,
                "limit": str(limit)
            }

            if start_time:
                params["before"] = int(start_time.timestamp() * 1000)
            if end_time:
                params["after"] = int(end_time.timestamp() * 1000)

            r = requests.get(base_url, params=params).json()
            rows = r['data']

            df = pd.DataFrame(rows, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume', 'quote_volume'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

            result[interval] = df.sort_index()

        except Exception:
            result[interval] = pd.DataFrame()

    return result, "Okx"
