# utils/format_symbol_for_okx.py
# version 2.0, aug 2025

def format_symbol_for_okx(symbol: str) -> str:
    symbol = symbol.upper()
    if "-" in symbol:
        return symbol

    for quote in ["USDT", "USDC", "BTC", "ETH", "EUR"]:
        if symbol.endswith(quote):
            base = symbol[:-len(quote)]
            return f"{base}-{quote}"
    return symbol
