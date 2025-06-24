# riskmanagement/riskmanagement_handler.py

from datetime import datetime
import pytz
import pandas as pd
from configs.config import TIMEZONE
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback
from riskmanagement.momentum_validator import verify_signal_with_momentum_and_volume
from riskmanagement.price_change_analyzer import calculate_price_changes, should_block_signal

def check_riskmanagement(symbol: str, signal: str, intervals=None, volume_multiplier=1.5):

    if intervals is None:
        intervals = [5]

    ohlcv_data, _ = fetch_ohlcv_fallback(symbol, intervals=["5m"], limit=30)
    if not ohlcv_data or "5m" not in ohlcv_data or ohlcv_data["5m"].empty:
        print("⚠️  Riskmanagement: No OHLCV data available.")
        return

    df = ohlcv_data["5m"]
    result = verify_signal_with_momentum_and_volume(df, signal, symbol, intervals=intervals)
    strength = result["momentum_strength"]
    interpretation = result.get("interpretation", "")

    # Hae nykyinen aika ja price change -data
    if isinstance(df.index, pd.DatetimeIndex):
        last_timestamp = df.index[-1]
        if last_timestamp.tzinfo is None:
            last_timestamp = last_timestamp.tz_localize('UTC')
        now = datetime.now(pytz.timezone(TIMEZONE.zone))
    else:
        now = datetime.now(pytz.timezone(TIMEZONE.zone))

    # Hinta muutos tarkistus
    price_changes = calculate_price_changes(symbol, now)
    if should_block_signal(signal, price_changes):
        return "none"
    print(f"📊 Price change % for {symbol} (from past): {price_changes}")

    # Tulosta momentum-analyysin tulos
    if strength == "strong":
        print(f"✅ Momentum to {signal} is STRONG")
    elif strength == "weak":
        print(f"🟡 Momentum to {signal} is WEAK")
    else:
        print(f"❌ Momentum to {signal} is NONE")

    return strength
