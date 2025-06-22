# riskmanagement/price_change_analyzer.py

import pandas as pd
from datetime import datetime, timedelta
import pytz
from configs.config import TIMEZONE
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback


def calculate_price_changes(symbol: str, current_time: datetime) -> dict:
    from configs.config import TIMEZONE
    import pytz

    # 🕒 Varmistetaan, että current_time on UTC-aikaa
    if current_time.tzinfo is None:
        current_time = pytz.timezone(TIMEZONE.zone).localize(current_time)
    current_time = current_time.astimezone(pytz.UTC)

    ohlcv_data, _ = fetch_ohlcv_fallback(symbol, intervals=["5m"], limit=300)

    if ohlcv_data is None or "5m" not in ohlcv_data or ohlcv_data["5m"].empty:
        print(f"⚠️ Ei OHLCV-dataa saatavilla symbolille {symbol}")
        return {}

    df = ohlcv_data["5m"].copy().reset_index()
    df.rename(columns={"timestamp": "timestamp", "close": "price"}, inplace=True)
    df = df[["timestamp", "price"]]
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    if df['timestamp'].dt.tz is None:
        df['timestamp'] = df['timestamp'].dt.tz_localize(pytz.UTC)  # OHLCV data oletetaan olevan UTC

    timeframes = {
        "24h": timedelta(hours=24),
        "18h": timedelta(hours=18),
        "12h": timedelta(hours=12),
        "6h": timedelta(hours=6),
        "4h": timedelta(hours=4),
        "3h": timedelta(hours=3),
        "2h": timedelta(hours=2),
    }

    result = {}
    current_row = df[df["timestamp"] <= current_time]
    if current_row.empty:
        return {key: None for key in timeframes}

    current_price = current_row.iloc[-1]["price"]

    for label, delta in timeframes.items():
        past_time = current_time - delta
        df["timedelta"] = (df["timestamp"] - past_time).abs()

        # Hae vain lähimmät datapisteet, joiden ero <= 10 minuuttia
        filtered_df = df[df["timedelta"] <= timedelta(minutes=10)]

        if filtered_df.empty:
            print(f"⚠️ [{label}] Ei sopivaa datapistettä (yli 10 min ero)")
            result[label] = None
            continue

        closest_row = filtered_df.loc[filtered_df["timedelta"].idxmin()]
        past_price = closest_row["price"]
        actual_time = closest_row["timestamp"]

        change_pct = ((current_price - past_price) / past_price) * 100
        result[label] = round(change_pct, 2)

        print(f"🔍 [{label}] Past price: {past_price}, Time: {actual_time}, Current price: {current_price}, Change: {result[label]}%")

    return result
