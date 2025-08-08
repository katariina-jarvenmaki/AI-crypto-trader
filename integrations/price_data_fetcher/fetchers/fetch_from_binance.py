# integrations/price_data_fetcher/price_data_from_binance.py

import requests

def fetch_from_binance(symbol):

    symbol = symbol.replace("USDC", "USDT")
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    r = requests.get(url)
    if r.status_code == 200:
        t = r.json()
        return {
            "lastPrice": float(t["lastPrice"]),
            "priceChangePercent": float(t["priceChangePercent"]),
            "highPrice": float(t["highPrice"]),
            "lowPrice": float(t["lowPrice"]),
            "volume": float(t["volume"]),
            "turnover": float(t["quoteVolume"]),
        }