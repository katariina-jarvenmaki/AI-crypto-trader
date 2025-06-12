# riskmanagement/riskmanagement_handler.py
from typing import List

from integrations.binance_api_client import fetch_ohlcv_for_intervals
from riskmanagement.momentum_validator import verify_signal_with_momentum_and_volume

def check_riskmanagement(symbol: str, signal: str, intervals=None):
    if intervals is None:
        intervals = [5, 15]

    ohlcv_data = fetch_ohlcv_for_intervals(symbol, intervals=["30m"], limit=30)
    if not ohlcv_data or "30m" not in ohlcv_data or ohlcv_data["30m"].empty:
        print("⚠️  Riskmanagement: No OHLCV data available.")
        return

    df = ohlcv_data["30m"]
    result = verify_signal_with_momentum_and_volume(df, signal, intervals=intervals)

    strength = result["momentum_strength"]
    merged_score = result.get("merged_score", None)
    interpretation = result.get("interpretation", "")

    print(f"📈 Merged momentum strength: {strength.upper()} (score: {merged_score})")

    if strength == "strong":
        print("✅ Momentum is STRONG → OK to act")
    elif strength == "weak":
        print("🟡 Momentum is WEAK → Optional, watch volume")
    else:
        print("❌ Momentum is NONE → Skip")

    return strength
