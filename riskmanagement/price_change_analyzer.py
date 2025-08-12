# riskmanagement/price_change_analyzer.py

import pandas as pd
from datetime import datetime, timedelta
import pytz
from configs.config import TIMEZONE, PRICE_CHANGE_LIMITS
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback

def check_price_change_risk(symbol: str, signal: str, df: pd.DataFrame) -> tuple[str, dict]:
    """
    Checks price changes and decides whether a signal should be blocked.
    Returns:
        - "none" if the signal is blocked
        - None if not blocked (continue risk management logic)
    """
    from datetime import datetime
    from configs.config import TIMEZONE
    import pytz

    # Determine the current timestamp
    if isinstance(df.index, pd.DatetimeIndex):
        last_timestamp = df.index[-1]
        if last_timestamp.tzinfo is None:
            last_timestamp = last_timestamp.tz_localize('UTC')
        now = datetime.now(pytz.timezone(TIMEZONE.zone))
    else:
        now = datetime.now(pytz.timezone(TIMEZONE.zone))

    # Calculate price changes
    price_changes = calculate_price_changes(symbol, now)
    if should_block_signal(signal, price_changes):
        return "none", price_changes

    print(f"🏷️  Price change % for {symbol} (from past): {price_changes}")
    return None, price_changes

def should_block_signal(signal: str, price_changes: dict) -> bool:

    limits = PRICE_CHANGE_LIMITS.get(signal, {})
    values = [v for v in price_changes.values() if v is not None]

    # Poikkeusten käsittely
    if not values:
        return False

    # Lasketaan kokonaissumma
    total_change = sum(values)
    # print(f"🏷️  Price total change % (from past): {total_change}")

    # Tarkistetaan, onko yksittäinen arvo ylittänyt "piikki"rajat
    has_spike = any(v > 6.0 for v in values)
    has_drop = any(v < -6.0 for v in values)

    # Estetään signaali, jos vastoin suuntaa:
    if signal == "buy":
        if total_change > 2.0 or has_spike:
            return True  # liian paljon nousua → ei hyvä ostopaikka
    elif signal == "sell":
        if total_change < -2.0 or has_drop:
            return True  # liikaa laskua → ei hyvä myyntipaikka

    # Lisäksi käytetään alkuperäisiä raja-arvoja (esim. `PRICE_CHANGE_LIMITS`)
    for timeframe, change in price_changes.items():

        if change is None:
            continue

        threshold = limits.get(timeframe)
        if threshold is None:
            continue

        if signal == "buy" and change > threshold:
            return True

        if signal == "sell" and change < threshold:
            return True

    return False

def calculate_price_changes(symbol: str, current_time: datetime) -> dict:
    from configs.config import TIMEZONE
    import pytz

    # 🕒 Ensure current_time is in UTC
    if current_time.tzinfo is None:
        current_time = pytz.timezone(TIMEZONE.zone).localize(current_time)
    current_time = current_time.astimezone(pytz.UTC)

    result = fetch_ohlcv_fallback(symbol, intervals=["5m"], limit=300)
    ohlcv_data = result.get("data_by_interval", {}) if result else {}

    if not ohlcv_data or "5m" not in ohlcv_data or ohlcv_data["5m"].empty:
        print(f"⚠️ No OHLCV data available for symbol {symbol}")
        return {}

    df = ohlcv_data["5m"].copy().reset_index()
    df.rename(columns={"timestamp": "timestamp", "close": "price"}, inplace=True)
    df = df[["timestamp", "price"]]
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    if df['timestamp'].dt.tz is None:
        df['timestamp'] = df['timestamp'].dt.tz_localize(pytz.UTC)  # Assume OHLCV data is in UTC

    timeframes = {
        "24h": timedelta(hours=24),
        "18h": timedelta(hours=18),
        "12h": timedelta(hours=12),
        "6h": timedelta(hours=6),
        "4h": timedelta(hours=4),
        "3h": timedelta(hours=3),
        "2h": timedelta(hours=2),
        "1h": timedelta(hours=1),
        "30min": timedelta(hours=0.5)
    }

    result = {}
    current_row = df[df["timestamp"] <= current_time]
    if current_row.empty:
        return {key: None for key in timeframes}

    current_price = current_row.iloc[-1]["price"]

    for label, delta in timeframes.items():
        past_time = current_time - delta
        df["timedelta"] = (df["timestamp"] - past_time).abs()

        # Only include datapoints within ±10 minutes
        filtered_df = df[df["timedelta"] <= timedelta(minutes=10)]

        if filtered_df.empty:
            print(f"⚠️ [{label}] No suitable datapoint found (difference > 10 minutes)")
            result[label] = None
            continue

        closest_row = filtered_df.loc[filtered_df["timedelta"].idxmin()]
        past_price = closest_row["price"]
        actual_time = closest_row["timestamp"]

        change_pct = ((current_price - past_price) / past_price) * 100
        result[label] = round(change_pct, 2)

        # print(f"🔍 [{label}] Past price: {past_price}, Time: {actual_time}, Current price: {current_price}, Change: {result[label]}%")

    return result