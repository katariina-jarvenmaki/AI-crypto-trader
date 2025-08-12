# integrations/multi_interval_ohlcv/fetch_ohlcv_okx_for_intervals.py
# version 2.0, aug 2025

import sys
import requests
import importlib
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# CONFIG INIT
from utils.format_symbol_for_okx import format_symbol_for_okx
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

def fetch_ohlcv_okx(symbol, intervals=None, limit=None, start_time=None, end_time=None):
    symbol = format_symbol_for_okx(symbol)
    intervals = intervals or config.get("interval_map_okx")
    limit = limit or config.get("ohlcv_limit")
    interval_map = config.get("interval_map_okx")
    base_url = config.get("okx_base_url", "https://www.okx.com/api/v5/market/candles")
    result = {}

    for interval in intervals:
        try:
            params = {
                "instId": symbol,
                "bar": interval_map[interval],
                "limit": str(limit)
            }

            if start_time:
                params["after"] = int(start_time.timestamp() * 1000)
            if end_time:
                params["before"] = int(end_time.timestamp() * 1000)

            response = requests.get(base_url, params=params)
            data = response.json()

            if data.get("code") != "0":
                result[interval] = pd.DataFrame()
                continue

            rows = data.get("data", [])
            if not rows:
                print(f"⚠️ No OHLCV data returned from OKX for {symbol} @ {interval}")
                result[interval] = pd.DataFrame()
                continue

            df = pd.DataFrame(rows, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'quote_volume', 'ignore1', 'ignore2'
            ])
            df['timestamp'] = pd.to_datetime(pd.to_numeric(df['timestamp']), unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

            result[interval] = df.sort_index()

        except Exception as e:
            print(f"❌ Exception while fetching {symbol} @ {interval} from OKX: {e}")
            result[interval] = pd.DataFrame()

    return result, "Okx"