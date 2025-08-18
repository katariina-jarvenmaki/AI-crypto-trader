# integrations/multi_interval_ohlcv/fetch_ohlcv_binance_for_intervals.py
# version 2.0, aug 2025

import sys
import time
import requests
import pandas as pd
from pathlib import Path
from binance.exceptions import BinanceAPIException
from requests.exceptions import ReadTimeout

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

def fetch_ohlcv_binance(symbol, intervals=None, limit=None, start_time=None, end_time=None):
    intervals = intervals or config.get("intervals")
    limit = limit or config.get("ohlcv_limit")
    base_url = config.get("binance_base_url", "https://api.binance.com/api/v3/klines")
    max_retries = config.get("fetch_retry", {}).get("max_retries", 3)
    retry_delay = config.get("fetch_retry", {}).get("retry_delay", 2)

    result = {}

    for interval in intervals:
        success = False
        for _ in range(max_retries):
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

                response = requests.get(base_url, params=params, timeout=10)
                response.raise_for_status()
                klines = response.json()

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

            except (requests.exceptions.RequestException, ValueError):
                time.sleep(retry_delay)

        if not success:
            raise Exception(f"Binance fetch failed for {symbol} ({interval})")

    return result, "Binance"
