# integrations/multi_interval_ohlcv/fetch_ohlcv_bybit_for_intervals.py
import requests
import pandas as pd
from configs.config import DEFAULT_INTERVALS, DEFAULT_OHLCV_LIMIT

def fetch_ohlcv_bybit(symbol, intervals=None, limit=None):
    intervals = intervals or DEFAULT_INTERVALS
    limit = limit or DEFAULT_OHLCV_LIMIT

    interval_map = {
        '1m': '1', '3m': '3', '5m': '5', '15m': '15', '30m': '30',
        '1h': '60', '2h': '120', '4h': '240', '1d': 'D', '1w': 'W'
    }

    base_url = "https://api.bybit.com/v5/market/kline"
    result = {}

    for interval in intervals:
        try:
            mapped = interval_map[interval]
            params = {
                "category": "spot",
                "symbol": symbol,
                "interval": mapped,
                "limit": limit
            }
            r = requests.get(base_url, params=params).json()
            rows = r['result']['list']

            df = pd.DataFrame(rows, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
            ])
            df['timestamp'] = pd.to_datetime(pd.to_numeric(df['timestamp']), unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

            result[interval] = df.sort_index()

        except Exception:
            result[interval] = pd.DataFrame()

    return result, "ByBit"

