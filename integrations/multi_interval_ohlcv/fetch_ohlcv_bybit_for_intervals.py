# integrations/multi_interval_ohlcv/fetch_ohlcv_bybit_for_intervals.py

import sys
import requests
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# CONFIG INIT
from modules.pathbuilder.pathbuilder import pathbuilder
from utils.config_reader import config_reader

general_config = config_reader()
paths = pathbuilder(extension=".json", file_name=general_config["module_filenames"]["multi_interval_ohlcv"], mid_folder="fetch")
config = config_reader(config_path = paths["full_config_path"], schema_path = paths["full_config_schema_path"])

def fetch_ohlcv_bybit(symbol, intervals=None, limit=None, start_time=None, end_time=None):
    intervals = intervals or config.get("interval_map_bybit")
    limit = limit or config.get("ohlcv_limit")
    interval_map = config.get("interval_map_bybit")
    base_url = config.get("bybit_base_url", "https://api.bybit.com/v5/market/kline")
    result = {}

    for interval in intervals:
        try:
            params = {
                "category": "spot",
                "symbol": symbol,
                "interval": interval_map[interval],
                "limit": limit
            }

            if start_time:
                params["start"] = int(start_time.timestamp() * 1000)
            if end_time:
                params["end"] = int(end_time.timestamp() * 1000)

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
