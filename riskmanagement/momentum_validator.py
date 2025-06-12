from typing import List

def verify_signal_with_momentum_and_volume(df, signal: str, intervals: List[int] = [5]) -> dict:
    """
    Tarkistaa onko signaali (buy/sell) tuettu hinnan ja volyymin perusteella eri aikavälien perusteella.
    Palauttaa dict, jossa tulkinta ja arvoja analyysiä varten.
    """
    result = {
        "momentum_strength": "none",  # default
        "momentum": None,
        "volume": None,
        "interpretation": "",
    }

    df['price_change'] = df['close'].diff()
    df['volume_change'] = df['volume'].diff()

    show_intervals = len(intervals) > 1

    for interval in intervals:
        recent_price_momentum = df['price_change'][-interval:].mean()
        previous_price_momentum = df['price_change'][-2*interval:-interval].mean()

        recent_volume = df['volume'][-interval:].mean()
        previous_volume = df['volume'][-2*interval:-interval].mean()

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

        if show_intervals:
            print(f"Interval: {interval} | Strength: {strength.upper()} | {interp}")

    # Tee päätös oletusintervalleilla, esim. [5]
    default_interval = 5
    recent_price_momentum = df['price_change'][-default_interval:].mean()
    previous_price_momentum = df['price_change'][-2*default_interval:-default_interval].mean()
    recent_volume = df['volume'][-default_interval:].mean()
    previous_volume = df['volume'][-2*default_interval:-default_interval].mean()

    result["momentum"] = (previous_price_momentum, recent_price_momentum)
    result["volume"] = (previous_volume, recent_volume)

    if signal.lower() == "buy":
        if recent_price_momentum > 0 and recent_volume > previous_volume:
            result["momentum_strength"] = "strong"
            result["interpretation"] = "Price turning up with increasing volume."
        elif recent_price_momentum > previous_price_momentum:
            result["momentum_strength"] = "weak"
            result["interpretation"] = "Downtrend weakening, but volume confirmation missing."
        else:
            result["momentum_strength"] = "none"
            result["interpretation"] = "No clear bullish shift."

    elif signal.lower() == "sell":
        if recent_price_momentum < 0 and recent_volume > previous_volume:
            result["momentum_strength"] = "strong"
            result["interpretation"] = "Price turning down with increasing volume."
        elif recent_price_momentum < previous_price_momentum:
            result["momentum_strength"] = "weak"
            result["interpretation"] = "Uptrend weakening, but no strong confirmation."
        else:
            result["momentum_strength"] = "none"
            result["interpretation"] = "No clear bearish shift."

    return result
