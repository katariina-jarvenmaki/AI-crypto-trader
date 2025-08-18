# integrations/price_data_fetcher/fetchers/fetch_from_okx.py
# version 2.0, aug 2025

import requests

def format_symbol_for_okx(symbol: str, quote_assets: str):

    for quote in quote_assets:
        if symbol.endswith(quote):
            base = symbol[:-len(quote)]
            return f"{base}-{quote}"
    return symbol

def fetch_from_okx(symbol, config):

    quote_assets  = config["okx"]["quote_assets"]
    base_url  = config["okx"]["base_url"]
    timeout  = config["okx"]["timeout"]
    symbol = format_symbol_for_okx(symbol, quote_assets)

    url = f"{base_url}?instId={symbol}"

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None

    if data.get('code') != '0':
        return None

    data = data.get('data', [])
    last = float(data[0]['last'])
    open_price = float(data[0]['open24h'])
    price_change_percent = ((last - open_price) / open_price * 100) if open_price else 0.0

    return {
        "lastPrice": data[0]['last'],
        "priceChangePercent": round(price_change_percent, 2),
        "highPrice": data[0]['high24h'],
        "lowPrice": data[0]['low24h'],
        "volume": data[0]['vol24h'],
        "turnover": data[0]['volCcy24h'],
    }
