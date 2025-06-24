# riskmanagement/riskmanagement_handler.py

from datetime import datetime
import pytz
import pandas as pd
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback
from riskmanagement.momentum_validator import verify_signal_with_momentum_and_volume
from riskmanagement.price_change_analyzer import check_price_change_risk

def check_riskmanagement(symbol: str, signal: str, market_state: str, override_signal: bool = False, intervals=None):

    if override_signal:
        return "strong"

    if intervals is None:
        intervals = [5]

    # Fetch OHLCV for timestamp reference
    ohlcv_data, _ = fetch_ohlcv_fallback(symbol, intervals=["5m"], limit=30)
    if not ohlcv_data or "5m" not in ohlcv_data or ohlcv_data["5m"].empty:
        print("⚠️  Riskmanagement: No OHLCV data available.")
        return
    df = ohlcv_data["5m"]

    # Price change risk check
    price_risk_result = check_price_change_risk(symbol, signal, df)
    if price_risk_result == "none":
        return "none"

    # Momentum and market check
    result = verify_signal_with_momentum_and_volume(df, signal, symbol, intervals=intervals, market_state=market_state)
    strength = result["momentum_strength"]
    interpretation = result.get("interpretation", "")

    # Print momentum analysis result
    if strength == "strong":
        print(f"✅ Momentum to {signal} is STRONG")
    elif strength == "weak":
        print(f"🟡 Momentum to {signal} is WEAK")
    else:
        print(f"❌ Momentum to {signal} is NONE")

    return strength