# integrations/multi_interval_ohlcv/fetch_ohlcv_binance_for_intervals.py
import pandas as pd
from binance.exceptions import BinanceAPIException
from configs.config import DEFAULT_INTERVALS, DEFAULT_OHLCV_LIMIT
from integrations.binance_api_client import client

def fetch_ohlcv_binance(symbol, intervals=None, limit=None):
    intervals = intervals or DEFAULT_INTERVALS
    limit = limit or DEFAULT_OHLCV_LIMIT
    result = {}

    for interval in intervals:
        try:
            klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
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

        except BinanceAPIException:
            result[interval] = pd.DataFrame()

    return result, "Binance"
