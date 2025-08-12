# integrations/multi_interval_ohlcv/fetch_ohlcv_kucoin_for_intervals.py
# version 2.0, aug 2025

import sys
import requests
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# CONFIG INIT
from utils.load_configs_and_logs import load_configs_and_logs 

configs_and_logs = load_configs_and_logs([
    {
        "name": "multi_interval_ohlcv",
        "mid_folder": "fetch",
        "module_key": "multi_interval_ohlcv",
        "extension": ".jsonl",
        "return": ["config", "full_log_path", "full_log_schema_path"]
    }
])

general_config = configs_and_logs["general_config"]
config = configs_and_logs["multi_interval_ohlcv_config"]
paths = {
    "full_log_path": configs_and_logs["multi_interval_ohlcv_full_log_path"],
    "full_log_schema_path": configs_and_logs["multi_interval_ohlcv_full_log_schema_path"]
}

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
