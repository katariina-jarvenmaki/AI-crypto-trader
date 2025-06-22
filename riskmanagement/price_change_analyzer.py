import pandas as pd
from datetime import datetime, timedelta
import pytz
from configs.config import TIMEZONE
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback


def calculate_price_changes(symbol: str, current_time: datetime) -> dict:
    """
    Laskee prosentuaalisen hinnan muutoksen nykyhetkeen verrattuna eri aikaväleillä yhdelle symbolille Binance-datan pohjalta.
    """
    # Haetaan 5m-kynttilöitä 24h ajalta (n. 288 kynttilää)
    ohlcv_data, _ = fetch_ohlcv_fallback(symbol, intervals=["5m"], limit=300)

    if ohlcv_data is None or "5m" not in ohlcv_data or ohlcv_data["5m"].empty:
        print(f"⚠️ Ei OHLCV-dataa saatavilla symbolille {symbol}")
        return {}

    df = ohlcv_data["5m"].copy().reset_index()
    df.rename(columns={"timestamp": "timestamp", "close": "price"}, inplace=True)
    df = df[["timestamp", "price"]]
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    if df['timestamp'].dt.tz is None:
        df['timestamp'] = df['timestamp'].dt.tz_localize(pytz.timezone(TIMEZONE.zone))

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
        past_data = df[df["timestamp"] <= past_time]

        if not past_data.empty:
            past_price = past_data.iloc[-1]["price"]
            actual_time = past_data.iloc[-1]["timestamp"]

            change_pct = ((current_price - past_price) / past_price) * 100
            result[label] = round(change_pct, 2)
        else:
            print(f"⚠️ No data found for {label} (<= {past_time.isoformat()})")
            result[label] = None

    return result
