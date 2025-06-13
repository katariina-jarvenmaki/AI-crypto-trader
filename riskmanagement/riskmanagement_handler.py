# riskmanagement/riskmanagement_handler.py

from typing import List
from integrations.binance_api_client import fetch_ohlcv_for_intervals
from riskmanagement.momentum_validator import verify_signal_with_momentum_and_volume

def check_riskmanagement(symbol: str, signal: str, intervals=None):

    # 5m interval request for volume check
    if intervals is None:
        intervals = [5]
    ohlcv_data = fetch_ohlcv_for_intervals(symbol, intervals=["5m"], limit=30)
    if not ohlcv_data or "5m" not in ohlcv_data or ohlcv_data["5m"].empty:
        print("⚠️  Riskmanagement: No OHLCV data available.")
        return

    # Verify the momentum / volume
    df = ohlcv_data["5m"]
    result = verify_signal_with_momentum_and_volume(df, signal, intervals=intervals)
    strength = result["momentum_strength"]
    interpretation = result.get("interpretation", "")

    # Print results
    if strength == "strong":
        print(f"✅ Momentum to {signal} is STRONG")
    elif strength == "weak":
        print(f"🟡 Momentum to {signal} is WEAK")
    else:
        print(f"❌ Momentum to {signal} is NONE")

    return strength
