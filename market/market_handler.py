# market/market_handler.py
from market.market_analyzer import MarketAnalyzer
from integrations.binance_api_client import fetch_ohlcv_for_intervals
import pandas as pd

def get_market_state(symbol: str) -> dict:

    market_info = {"state": None, "started_on": None}

    # Get the OHLCV-data for "1h" interval
    ohlcv_data = fetch_ohlcv_for_intervals(symbol, intervals=["1h"], limit=100)
    df = ohlcv_data.get("1h")

    if df is None or df.empty:
        print(f"[ERROR] No data found for {symbol}")
        return

    # Create MarketAnalyzer
    analyzer = MarketAnalyzer(df, timeframe="1h")

    # Check the Market state
    market_state_data = analyzer.get_market_state_with_start_date()
    market_info["state"] = market_state_data["state"]
    market_info["started_on"] = market_state_data["started_on"]

    # Inform user about the market state
    print(f"📊 Market state: {market_info['state']}, started on: {market_info['started_on']}")
    return market_info
