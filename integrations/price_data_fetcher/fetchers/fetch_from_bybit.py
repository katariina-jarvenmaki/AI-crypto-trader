# integrations/price_data_fetcher/fetchers/fetch_from_bybit.py
# version 2.0, aug 2025

import requests

def fetch_from_bybit(symbol, config):

    symbol = symbol.replace("-", "")
    base_url = config["bybit"]["base_url"]
    timeout = config["bybit"]["timeout"]
    url = f"{base_url}&symbol={symbol}"

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        if data.get("retCode") == 0 and data.get("result") and data["result"].get("list"):
            row = data["result"]["list"][0]
            price_change_percent = float(row["price24hPcnt"]) * 100

            return {
                "lastPrice": row["lastPrice"],
                "priceChangePercent": round(price_change_percent, 2),
                "highPrice": row["highPrice24h"],
                "lowPrice": row["lowPrice24h"],
                "volume": row["volume24h"],
                "turnover": row["turnover24h"]
            }

    except (requests.RequestException, ValueError, KeyError) as e:
        pass

    return None