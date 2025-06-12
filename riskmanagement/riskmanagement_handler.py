from typing import List
from integrations.binance_api_client import fetch_ohlcv_for_intervals
from riskmanagement.momentum_validator import verify_signal_with_momentum_and_volume

def check_riskmanagement(symbol: str, signal: str, intervals=None):
    if intervals is None:
        intervals = [5]  # Käytä vain 5min

    ohlcv_data = fetch_ohlcv_for_intervals(symbol, intervals=["5m"], limit=30)
    if not ohlcv_data or "5m" not in ohlcv_data or ohlcv_data["5m"].empty:
        print("⚠️  Riskmanagement: No OHLCV data available.")
        return

    df = ohlcv_data["5m"]
    result = verify_signal_with_momentum_and_volume(df, signal, intervals=intervals)

    strength = result["momentum_strength"]
    interpretation = result.get("interpretation", "")

    # print(f"📈 5min momentum strength: {strength.upper()} → {interpretation}")

    if strength == "strong":
        print(f"✅ Momentum ({signal}) is STRONG")
    elif strength == "weak":
        print(f"🟡 Momentum ({signal}) is WEAK")
    else:
        print(f"❌ Momentum ({signal}) is NONE")

    return strength
