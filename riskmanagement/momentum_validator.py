from typing import List, Dict
import pandas as pd

def verify_signal_with_momentum_and_volume(df: pd.DataFrame, signal: str, intervals: List[int] = [5]) -> dict:
    """
    Tarkistaa onko signaali (buy/sell) tuettu hinnan ja volyymin perusteella eri aikavälien perusteella.
    Palauttaa dict, jossa tulkinta ja arvoja analyysiä varten.
    """

    result = {
        "momentum_strength": "none",
        "momentum": None,
        "volume": None,
        "interpretation": "",
        "per_interval": {},          # strength per interval
        "merged_score": 0.0,         # weighted numerical score
    }

    df['price_change'] = df['close'].diff()
    df['volume_change'] = df['volume'].diff()

    strength_map = {"none": 0, "weak": 1, "strong": 2}
    inverse_map = {0: "none", 1: "weak", 2: "strong"}

    strength_scores = []
    interval_weights = []

    total_weight = sum(intervals)  # käytetään painotusta suhteessa aikaväliin

    for interval in intervals:
        recent_price_momentum = df['price_change'][-interval:].mean()
        previous_price_momentum = df['price_change'][-2*interval:-interval].mean()
        recent_volume = df['volume'][-interval:].mean()
        previous_volume = df['volume'][-2*interval:-interval].mean()

        # Signaalianalyysi
        if signal.lower() == "buy":
            if recent_price_momentum > 0 and recent_volume > previous_volume:
                strength = "strong"
                interp = "Price turning up with increasing volume."
            elif recent_price_momentum > previous_price_momentum:
                strength = "weak"
                interp = "Downtrend weakening, but volume confirmation missing."
            else:
                strength = "none"
                interp = "No clear bullish shift."

        elif signal.lower() == "sell":
            if recent_price_momentum < 0 and recent_volume > previous_volume:
                strength = "strong"
                interp = "Price turning down with increasing volume."
            elif recent_price_momentum < previous_price_momentum:
                strength = "weak"
                interp = "Uptrend weakening, but no strong confirmation."
            else:
                strength = "none"
                interp = "No clear bearish shift."
        else:
            strength = "unknown"
            interp = "Unknown signal."

        # Painotettu laskenta
        weight = interval / total_weight
        strength_score = strength_map.get(strength, 0)

        strength_scores.append(strength_score * weight)
        interval_weights.append(weight)
        result["per_interval"][f"{interval}min"] = {
            "strength": strength,
            "momentum": (previous_price_momentum, recent_price_momentum),
            "volume": (previous_volume, recent_volume),
            "comment": interp
        }

        print(f"Interval: {interval} | Strength: {strength.upper()} | {interp}")

    # Laske yhdistetty (merge) strength
    if sum(interval_weights) > 0:
        weighted_score = sum(strength_scores) / sum(interval_weights)
    else:
        weighted_score = 0.0

    # Tulkinta arvoille
    if weighted_score >= 1.5:
        merged_strength = "strong"
    elif weighted_score >= 0.5:
        merged_strength = "weak"
    else:
        merged_strength = "none"

    # Päivitä tulokset
    result["momentum_strength"] = merged_strength
    result["merged_score"] = round(weighted_score, 2)
    result["interpretation"] = f"Merged strength based on {', '.join(str(i)+'min' for i in intervals)}: {merged_strength.upper()}"

    return result
