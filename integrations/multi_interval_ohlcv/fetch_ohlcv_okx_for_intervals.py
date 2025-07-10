# integrations/multi_interval_ohlcv/fetch_ohlcv_okx_for_intervals.py

import requests
import pandas as pd
from configs.config import DEFAULT_INTERVALS, DEFAULT_OHLCV_LIMIT

def format_symbol_for_okx(symbol: str) -> str:
    symbol = symbol.upper()
    if "-" in symbol:
        return symbol

    for quote in ["USDT", "USDC", "BTC", "ETH", "EUR"]:
        if symbol.endswith(quote):
            base = symbol[:-len(quote)]
            return f"{base}-{quote}"
    return symbol

def fetch_ohlcv_okx(symbol, intervals=None, limit=None, start_time=None, end_time=None):

    symbol = format_symbol_for_okx(symbol)  # Already handles formatting!
    intervals = intervals or DEFAULT_INTERVALS
    limit = limit or DEFAULT_OHLCV_LIMIT
    interval_map = {
        '1m': '1m', '3m': '3m', '5m': '5m', '15m': '15m',
        '30m': '30m', '1h': '1H', '2h': '2H', '4h': '4H',
        '1d': '1D', '1w': '1W'
    }

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

            # ✅ Corrected timestamp mapping
            if start_time:
                params["after"] = int(start_time.timestamp() * 1000)
            if end_time:
                params["before"] = int(end_time.timestamp() * 1000)

            # ⬇️ Make the request
            response = requests.get(base_url, params=params)
            data = response.json()

            # ✅ Validate API response
            if data.get("code") != "0":
                print(f"❌ OKX API error for {symbol} @ {interval}: {data.get('msg')}")
                result[interval] = pd.DataFrame()
                continue

            rows = data.get("data", [])
            if not rows:
                print(f"⚠️ No OHLCV data returned from OKX for {symbol} @ {interval}")
                result[interval] = pd.DataFrame()
                continue

            # ✅ Parse DataFrame
            df = pd.DataFrame(rows, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume', 'quote_volume', 'ignore1', 'ignore2'
            ])

            df['timestamp'] = pd.to_datetime(pd.to_numeric(df['timestamp']), unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

            result[interval] = df.sort_index()

        except Exception as e:
            print(f"❌ Exception while fetching {symbol} @ {interval} from OKX: {e}")
            result[interval] = pd.DataFrame()

    return result, "Okx"
