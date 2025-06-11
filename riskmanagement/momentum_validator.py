# riskmanagement/momentum_validator.py

def verify_signal_with_momentum_and_volume(df, signal: str) -> dict:
    """
    Tarkistaa onko signaali (buy/sell) tuettu hinnan ja volyymin perusteella.
    Palauttaa dict, jossa tulkinta ja arvoja analyysiä varten.
    """
    result = {
        "signal_strength": "none",  # default
        "momentum": None,
        "volume": None,
        "interpretation": "",
    }

    df['price_change'] = df['close'].diff()
    df['volume_change'] = df['volume'].diff()

    recent_price_momentum = df['price_change'][-5:].mean()
    previous_price_momentum = df['price_change'][-10:-5].mean()

    recent_volume = df['volume'][-5:].mean()
    previous_volume = df['volume'][-10:-5].mean()

    result["momentum"] = (previous_price_momentum, recent_price_momentum)
    result["volume"] = (previous_volume, recent_volume)

    if signal.lower() == "buy":
        if recent_price_momentum > 0 and recent_volume > previous_volume:
            result["signal_strength"] = "strong"
            result["interpretation"] = "Price turning up with increasing volume."
        elif recent_price_momentum > previous_price_momentum:
            result["signal_strength"] = "weak"
            result["interpretation"] = "Downtrend weakening, but volume confirmation missing."
        else:
            result["signal_strength"] = "none"
            result["interpretation"] = "No clear bullish shift."
    
    elif signal.lower() == "sell":
        if recent_price_momentum < 0 and recent_volume > previous_volume:
            result["signal_strength"] = "strong"
            result["interpretation"] = "Price turning down with increasing volume."
        elif recent_price_momentum > previous_price_momentum:
            result["signal_strength"] = "weak"
            result["interpretation"] = "Uptrend weakening, but no strong confirmation."
        else:
            result["signal_strength"] = "none"
            result["interpretation"] = "No clear bearish shift."

    return result
