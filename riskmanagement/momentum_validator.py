#riskmanagement/momentum_validator.py

from typing import List, Dict
import pandas as pd
from configs.config import VOLUME_MULTIPLIERS

def verify_signal_with_momentum_and_volume(
    df: pd.DataFrame,
    signal: str,
    symbol: str,
    intervals: List[int] = [5],
    market_state: str = None,
    volume_multiplier: float = None
) -> dict:
    result = {
        "momentum_strength": "none",
        "momentum": None,
        "volume": None,
        "interpretation": "",
        "per_interval": {},
    }

    df['price_change'] = df['close'].diff()
    df['volume_change'] = df['volume'].diff()

    # Hae default multiplier configista
    config_multiplier = VOLUME_MULTIPLIERS.get(symbol.upper(), {}).get(signal.lower())
    if volume_multiplier is None:
        volume_multiplier = config_multiplier if config_multiplier is not None else 1.0  # fallback default

    # 🔁 Mukauta multiplier markkinatilanteen mukaan
    if market_state == "bull" and signal == "sell":
        volume_multiplier += 0.3
    elif market_state == "bear" and signal == "buy":
        volume_multiplier += 0.3
    elif market_state == "unknown" and signal == "sell":
        volume_multiplier += 0.2
    elif market_state == "unknown" and signal == "buy":
        volume_multiplier += 0.2
    elif market_state == "neutral_sideways" and signal == "sell":
        volume_multiplier += 0.2
    elif market_state == "neutral_sideways" and signal == "buy":
        volume_multiplier += 0.2
    elif market_state == "bull" and signal == "buy":
        volume_multiplier -= 0.1
    elif market_state == "bear" and signal == "sell":
        volume_multiplier -= 0.1

    for interval in intervals:
        recent_price_momentum = df['price_change'][-interval:].mean()
        previous_price_momentum = df['price_change'][-2*interval:-interval].mean()
        recent_volume = df['volume'][-interval:].mean()
        previous_volume = df['volume'][-2*interval:-interval].mean()

        volume_condition = recent_volume > volume_multiplier * previous_volume

        if signal.lower() == "buy":
            if recent_price_momentum > 0 and volume_condition:
                strength = "strong"
                interp = "Price turning up with significantly increasing volume."
            elif recent_price_momentum > previous_price_momentum:
                strength = "weak"
                interp = "Downtrend weakening, but volume confirmation missing."
            else:
                strength = "none"
                interp = "No clear bullish shift."
        elif signal.lower() == "sell":
            if recent_price_momentum < 0 and volume_condition:
                strength = "strong"
                interp = "Price turning down with significantly increasing volume."
            elif recent_price_momentum < previous_price_momentum:
                strength = "weak"
                interp = "Uptrend weakening, but no strong confirmation."
            else:
                strength = "none"
                interp = "No clear bearish shift."
        else:
            strength = "unknown"
            interp = "Unknown signal."

        result["momentum_strength"] = strength
        result["interpretation"] = interp
        result["momentum"] = (previous_price_momentum, recent_price_momentum)
        result["volume"] = (previous_volume, recent_volume)
        result["per_interval"][f"{interval}min"] = {
            "strength": strength,
            "momentum": result["momentum"],
            "volume": result["volume"],
            "comment": interp
        }

        # print(f"🔁 Used volume multiplier for {interval}min interval: {volume_multiplier} with {market_state} market state")

    result["volume_multiplier"] = volume_multiplier
    return result