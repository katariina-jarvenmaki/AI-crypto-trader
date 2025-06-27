# riskmanagement/riskmanagement_handler.py

from datetime import datetime
import pytz
import pandas as pd
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback
from riskmanagement.momentum_validator import verify_signal_with_momentum_and_volume
from riskmanagement.price_change_analyzer import check_price_change_risk

def check_riskmanagement(symbol: str, signal: str, market_state: str, override_signal: bool = False, intervals=None, mode: str = None):
    
    if override_signal:
        # return dummy defaults in override mode
        return "strong", {}, 1.0, {"momentum_strength": "n/a", "interpretation": "override mode"}

    # Market state check for momentum-mode
    if mode == "momentum":
        allowed_states_for_buy = ["bull", "neutral_sideways", "volatile"]
        allowed_states_for_sell = ["bear", "unknown", "volatile"]

        if signal == "buy" and market_state not in allowed_states_for_buy:
            print(f"❌ Momentum BUY blocked by market state '{market_state}'")
            return "none", {}, 1.0, {}

        if signal == "sell" and market_state not in allowed_states_for_sell:
            print(f"❌ Momentum SELL blocked by market state '{market_state}'")
            return "none", {}, 1.0, {}

    if intervals is None:
        intervals = [5]

    # Fetch OHLCV for timestamp reference
    ohlcv_data, _ = fetch_ohlcv_fallback(symbol, intervals=["5m"], limit=30)
    if not ohlcv_data or "5m" not in ohlcv_data or ohlcv_data["5m"].empty:
        print("⚠️  Riskmanagement: No OHLCV data available.")
        return "none", {}, 1.0, {}

    df = ohlcv_data["5m"]

    # Price change risk check
    price_risk_result, price_changes = check_price_change_risk(symbol, signal, df)
    if price_risk_result == "none":
        print(f"⛔ Blocked {signal.upper()} signal: [2h] Change {price_changes.get('2h')}% exceeds threshold.")
        return "none", price_changes, 1.0, {"momentum_strength": "n/a", "interpretation": "price change block"}

    # Momentum and market check
    result = verify_signal_with_momentum_and_volume(df, signal, symbol, intervals=intervals, market_state=market_state)
    strength = result["momentum_strength"]
    volume_multiplier = result.get("volume_multiplier", 1.0)
    interpretation = result.get("interpretation", "")

    # Reverse signal analysis 15min
    reverse_signal = "sell" if signal == "buy" else "buy"
    ohlcv_15m_data, _ = fetch_ohlcv_fallback(symbol, intervals=["15m"], limit=30)
    reverse_result = {}
    if ohlcv_15m_data and "15m" in ohlcv_15m_data and not ohlcv_15m_data["15m"].empty:
        df_15m = ohlcv_15m_data["15m"]
        reverse_result = verify_signal_with_momentum_and_volume(df_15m, reverse_signal, symbol, intervals=[15], market_state=market_state)
    else:
        reverse_result = {"momentum_strength": "n/a", "interpretation": "No 15m OHLCV"}

    # Print momentum analysis result
    print(f"✅ Momentum to {signal.upper()} is {strength.upper()}")
    print(f"↩️  Reverse momentum {reverse_signal.upper()} is {reverse_result.get('momentum_strength', 'n/a').upper()}")

    return strength, price_changes, volume_multiplier, reverse_result
