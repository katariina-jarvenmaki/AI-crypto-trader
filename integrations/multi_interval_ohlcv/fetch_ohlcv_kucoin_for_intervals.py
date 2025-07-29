# integrations/multi_interval_ohlcv/fetch_ohlcv_kucoin_for_intervals.py

import sys
import requests
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# CONFIG INIT
from utils.config_reader import config_reader

config = config_reader(extension=".json", file_name="multi_ohlcv_fetch", mid_folder="fetch")

def fetch_ohlcv_kucoin(symbol, intervals=None, limit=None, start_time=None, end_time=None):
    symbol = symbol.replace("USDT", "-USDT")
    intervals = intervals or config.get("interval_map_kucoin")
    limit = limit or config.get("ohlcv_limit")
    interval_map = config.get("interval_map_kucoin")
    base_url = config.get("kucoin_base_url", "https://api.kucoin.com/api/v1/market/candles")
    result = {}

    for interval in intervals:
        try:
            params = {
                "type": interval_map[interval],
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
