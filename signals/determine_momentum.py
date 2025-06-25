# signals/determine_momentum.py

from typing import List
import pandas as pd
from configs.config import VOLUME_MULTIPLIERS

def determine_signal_with_momentum_and_volume(
    df: pd.DataFrame,
    symbol: str,
    intervals: List[int] = [5],
    volume_multiplier: float = None  # None tarkoittaa: käytä conffia
) -> dict:
    result = {
        "suggested_signal": "none",
        "momentum_strength": "none",
        "momentum": None,
        "volume": None,
        "interpretation": "",
        "per_interval": {},
    }

    df['price_change'] = df['close'].diff()
    df['volume_change'] = df['volume'].diff()

    best_strength = "none"
    best_signal = "none"
    final_interp = ""

    config_multiplier = VOLUME_MULTIPLIERS.get(symbol.upper(), {}).get("buy")
    vm = volume_multiplier if volume_multiplier is not None else (config_multiplier if config_multiplier is not None else default_volume_multiplier)

    for interval in intervals:
        recent_price_momentum = df['price_change'][-interval:].mean()
        previous_price_momentum = df['price_change'][-2*interval:-interval].mean()
        recent_volume = df['volume'][-interval:].mean()
        previous_volume = df['volume'][-2*interval:-interval].mean()

        volume_condition = recent_volume > vm * previous_volume

        if recent_price_momentum > 0:
            if volume_condition:
                strength = "strong"
                signal = "buy"
                interp = "Price turning up with significantly increasing volume."
            elif recent_price_momentum > previous_price_momentum:
                strength = "weak"
                signal = "buy"
                interp = "Downtrend weakening, but volume confirmation missing."
            else:
                strength = "none"
                signal = "none"
                interp = "No clear bullish signal."
        elif recent_price_momentum < 0:
            if volume_condition:
                strength = "strong"
                signal = "sell"
                interp = "Price turning down with significantly increasing volume."
            elif recent_price_momentum < previous_price_momentum:
                strength = "weak"
                signal = "sell"
                interp = "Uptrend weakening, but no strong confirmation."
            else:
                strength = "none"
                signal = "none"
                interp = "No clear bearish signal."
        else:
            strength = "none"
            signal = "none"
            interp = "Sideways movement."

        if strength == "strong":
            best_strength = strength
            best_signal = signal
            final_interp = interp
        elif strength == "weak" and best_strength != "strong":
            best_strength = strength
            best_signal = signal
            final_interp = interp

        result["per_interval"][f"{interval}min"] = {
            "suggested_signal": signal,
            "strength": strength,
            "momentum": (previous_price_momentum, recent_price_momentum),
            "volume": (previous_volume, recent_volume),
            "comment": interp
        }

    result["suggested_signal"] = best_signal
    result["momentum_strength"] = best_strength
    result["interpretation"] = final_interp
    result["volume_multiplier"] = vm

    return result
