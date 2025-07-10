# integrations/price_data_fetcher/price_data_from_kucoin.py

import requests

def format_symbol_for_kucoin(symbol: str) -> str:
    
    for quote in ["USDT", "USDC", "BTC", "ETH", "EUR"]:
        if symbol.endswith(quote):
            base = symbol[:-len(quote)]
            return f"{base}-{quote}"
    return symbol

def fetch_from_kucoin(symbol):
    symbol = format_symbol_for_kucoin(symbol)
    url = f"https://api.kucoin.com/api/v1/market/stats?symbol={symbol}"
    r = requests.get(url)
    data = r.json()
    if data['code'] == '200000':
        t = data['data']
        return {
            "lastPrice": float(t.get("last") or 0),
            "priceChangePercent": float(t.get("changeRate") or 0) * 100,
            "highPrice": float(t.get("high") or 0),
            "lowPrice": float(t.get("low") or 0),
            "volume": float(t.get("vol") or 0),
            "turnover": float(t.get("volValue") or 0),
        }

