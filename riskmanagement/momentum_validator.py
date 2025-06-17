from typing import List, Dict
import pandas as pd

def verify_signal_with_momentum_and_volume(
    df: pd.DataFrame,
    signal: str,
    intervals: List[int] = [5],
    volume_multiplier: float = 1.2  # 👈 Default / test value
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

    for interval in intervals:
        recent_price_momentum = df['price_change'][-interval:].mean()
        previous_price_momentum = df['price_change'][-2*interval:-interval].mean()
        recent_volume = df['volume'][-interval:].mean()
        previous_volume = df['volume'][-2*interval:-interval].mean()

        # 🧠 Käytetään volyymikerrointa
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

    return result
