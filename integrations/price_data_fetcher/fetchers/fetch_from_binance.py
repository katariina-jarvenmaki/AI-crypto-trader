# integrations/price_data_fetcher/fetchers/fetch_from_binance.py
# version 2.0, aug 2025

import requests

def fetch_from_binance(symbol, config):

    symbol = symbol.replace("USDC", "USDT")
    base_url = config["binance"]["base_url"]
    timeout = config["binance"]["timeout"]
    url = f"{base_url}?symbol={symbol}"

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        price_change_percent = float(data["priceChangePercent"])

        return {
            "lastPrice": data["lastPrice"],
            "priceChangePercent": round(price_change_percent, 2),
            "highPrice": data["highPrice"],
            "lowPrice": data["lowPrice"],
            "volume": data["volume"],
            "turnover": data["quoteVolume"],
        }
    except (requests.RequestException, ValueError, KeyError):
        return None
