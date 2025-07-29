# integrations/multi_interval_ohlcv/fetch_ohlcv_binance_for_intervals.py

import sys
import time
import requests
import pandas as pd
from pathlib import Path
from binance.exceptions import BinanceAPIException
from requests.exceptions import ReadTimeout

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# CONFIG INIT
from modules.pathbuilder.pathbuilder import pathbuilder
from utils.config_reader import config_reader

general_config = config_reader()
paths = pathbuilder(extension=".json", file_name=general_config["module_filenames"]["multi_interval_ohlcv"], mid_folder="fetch")
config = config_reader(config_path = paths["full_config_path"], schema_path = paths["full_schema_path"])

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
