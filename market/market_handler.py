# market/market_handler.py

from market.market_analyzer import MarketAnalyzer
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback
import pandas as pd

def get_market_state(symbol: str) -> dict:
    market_info = {"state": None, "started_on": None}

    # Get the OHLCV-data for "1h" interval
    result = fetch_ohlcv_fallback(symbol, intervals=["1h"], limit=100)
    if not result:
        print(f"[ERROR] No data found for {symbol}")
        return market_info

    ohlcv_data = result.get("data_by_interval", {})
    df = ohlcv_data.get("1h")

    if df is None or df.empty:
        print(f"[ERROR] No data found for {symbol}")
        return market_info

    # Create MarketAnalyzer
    analyzer = MarketAnalyzer(df, timeframe="1h")

    # Check the Market state
    market_state_data = analyzer.get_market_state_with_start_date()
    market_info["state"] = market_state_data["state"]
    market_info["started_on"] = market_state_data["started_on"]

    # Inform user about the market state
    return market_info
