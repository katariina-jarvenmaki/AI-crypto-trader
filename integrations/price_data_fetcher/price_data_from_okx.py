# integrations/price_data_fetcher/price_data_from_okx.py

import requests

def format_symbol_for_okx(symbol: str) -> str:

    for quote in ["USDT", "USDC", "BTC", "ETH", "EUR"]:
        if symbol.endswith(quote):
            base = symbol[:-len(quote)]
            return f"{base}-{quote}"
    return symbol

def fetch_from_okx(symbol):

    symbol = format_symbol_for_okx(symbol)
    url = f"https://www.okx.com/api/v5/market/ticker?instId={symbol}"
    r = requests.get(url)
    data = r.json()

    if data['code'] == '0' and data.get("data"):
        t = data['data'][0]

        last = float(t["last"])
        open_price = float(t["open24h"])
        price_change_percent = ((last - open_price) / open_price * 100) if open_price else 0.0

        return {
            "lastPrice": last,
            "priceChangePercent": round(price_change_percent, 2),
            "highPrice": float(t["high24h"]),
            "lowPrice": float(t["low24h"]),
            "volume": float(t["vol24h"]),
            "turnover": float(t["volCcy24h"]),
        }
