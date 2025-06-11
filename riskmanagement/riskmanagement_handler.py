# riskmanagement/riskmanagement_handler.py

from integrations.binance_api_client import fetch_ohlcv_for_intervals
from riskmanagement.momentum_validator import verify_signal_with_momentum_and_volume

def check_riskmanagement(symbol: str, signal: str):
    print(f"Riskmanagement for {symbol} {signal}")

    ohlcv_data = fetch_ohlcv_for_intervals(symbol, intervals=["1h"], limit=30)
    if not ohlcv_data or "1h" not in ohlcv_data or ohlcv_data["1h"].empty:
        print("⚠️ No OHLCV data available.")
        return

    df = ohlcv_data["1h"]
    result = verify_signal_with_momentum_and_volume(df, signal)

    print(f"📈 Price momentum: {result['momentum'][0]:.4f} → {result['momentum'][1]:.4f}")
    print(f"📊 Volume: {result['volume'][0]:.0f} → {result['volume'][1]:.0f}")
    print(f"🧠 Interpretation: {result['interpretation']}")

    strength = result["momentum_strength"]
    if strength == "strong":
        print("✅ Signal is STRONG → OK to act.")
    elif strength == "weak":
        print("🟡 Signal is WEAK → Optional, watch volume.")
    else:
        print("❌ Signal is NONE → Skip or monitor.")

    return strength 