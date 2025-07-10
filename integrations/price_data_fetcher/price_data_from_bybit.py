# integrations/price_data_fetcher/price_data_from_bybit.py

import requests

def fetch_from_bybit(symbol):
    
    symbol = symbol.replace("-", "")
    url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}"
    r = requests.get(url)
    print(f"[DEBUG] Bybit response ({r.status_code}): {r.text}")
    data = r.json()
    if data.get("retCode") == 0 and data.get("result") and data["result"].get("list"):
        t = data["result"]["list"][0]
        return {
            "lastPrice": float(t["lastPrice"]),
            "priceChangePercent": float(t.get("price24hPcnt", 0)) * 100,
            "highPrice": float(t["highPrice24h"]),      # <- korjattu
            "lowPrice": float(t["lowPrice24h"]),        # <- korjattu
            "volume": float(t["volume24h"]),
            "turnover": float(t["turnover24h"]),
        }
