# integrations/price_data_fetcher/fetchers/fetch_from_kucoin.py
# version 2.0, aug 2025

import requests
from typing import Dict, Optional, Any

def format_symbol_for_kucoin(symbol: str, quote_assets: str):
    
    for quote in quote_assets:
        if symbol.endswith(quote):
            base = symbol[:-len(quote)]
            return f"{base}-{quote}"
    return symbol

def fetch_from_kucoin(symbol, config):

    quote_assets  = config["kucoin"]["quote_assets"]
    base_url  = config["kucoin"]["base_url"]
    timeout  = config["kucoin"]["timeout"]
    formatted_symbol = format_symbol_for_kucoin(symbol, quote_assets)
    url = f"{base_url}?symbol={formatted_symbol}"

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None

    if data.get("code") != "200000":
        return None

    ticker = data.get("data", {})
    price_change_percent = float(ticker.get("changeRate") or 0) * 100

    return {
        "lastPrice": ticker.get("last") or 0,
        "priceChangePercent": round(price_change_percent, 2),
        "highPrice": ticker.get("high") or 0,
        "lowPrice": ticker.get("low") or 0,
        "volume": ticker.get("vol") or 0,
        "turnover": ticker.get("volValue") or 0,
    }