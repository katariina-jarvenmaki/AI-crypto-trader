# integrations/price_data_fetcher/price_data_from_okx.py
# version 2.0, aug 2025

import requests
from typing import Dict, Any

def format_symbol_for_okx(symbol: str, quote_assets: list[str]) -> str:
    """
    Muuntaa symbolin OKX:n formaattiin esim. BTCUSDT -> BTC-USDT.
    """
    for quote in quote_assets:
        if symbol.endswith(quote):
            base = symbol[:-len(quote)]
            return f"{base}-{quote}"
    return symbol

def fetch_from_okx(symbol: str, config: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    Hakee hinnan OKX API:sta ja palauttaa sanakirjan.
    Config-parametri määrittelee quote-listan ja API-pohja-URL:n.
    """
    symbol = format_symbol_for_okx(symbol, config["quote_assets"])
    url = f"{config['base_url']}?instId={symbol}"

    r = requests.get(url, timeout=config.get("timeout", 5))
    r.raise_for_status()
    data = r.json()

    if data.get('code') == '0' and data.get("data"):
        t = data['data'][0]

        last = float(t["last"])
        open_price = float(t["open24h"])
        price_change_percent = (
            (last - open_price) / open_price * 100
            if open_price else 0.0
        )

        return {
            "lastPrice": last,
            "priceChangePercent": round(price_change_percent, 2),
            "highPrice": float(t["high24h"]),
            "lowPrice": float(t["low24h"]),
            "volume": float(t["vol24h"]),
            "turnover": float(t["volCcy24h"]),
        }
    return None
