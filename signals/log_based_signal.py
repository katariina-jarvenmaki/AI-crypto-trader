# signals/log_based_signal.py

from scripts.signal_limiter import load_signal_log
from datetime import datetime, timedelta
import pytz
import pandas as pd
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback
from configs.config import (
    TIMEZONE,
    LOG_BASED_SIGNAL_TIMEOUT,
    RSI_FILTER_ENABLED,
    RSI_FILTER_INTERVAL,
    RSI_FILTER_PERIOD,
    RSI_FILTER_BUY_MAX,
    RSI_FILTER_SELL_MIN
)

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_log_based_signal(symbol: str) -> dict:
    log = load_signal_log()
    now = datetime.now(pytz.timezone(TIMEZONE.zone))
    symbol_log = log.get(symbol, {})

    if not symbol_log:
        return {}

    valid_entries = []

    for interval, signals in symbol_log.items():
        for signal_type in ['buy', 'sell']:
            signal_modes = signals.get(signal_type)
            if not isinstance(signal_modes, dict):
                continue

            for mode_name, mode_data in signal_modes.items():
                if not isinstance(mode_data, dict):
                    continue

                if mode_data.get("status") == "complete":
                    continue

                time_str = mode_data.get("time") or mode_data.get("rsi") or mode_data.get("timestamp") or mode_data.get("datetime")
                if not time_str:
                    continue

                try:
                    ts = datetime.fromisoformat(time_str)
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(TIMEZONE.zone))
                except ValueError:
                    continue

                if now - ts > LOG_BASED_SIGNAL_TIMEOUT:
                    continue

                valid_entries.append({
                    "signal": signal_type,
                    "interval": interval,
                    "mode": mode_name,
                    "time": ts
                })

    if not valid_entries:
        return {}

    def interval_sort_key(entry):
        unit_weight = {"m": 1, "h": 60, "d": 1440}
        try:
            num = int(''.join(filter(str.isdigit, entry["interval"])))
            unit = ''.join(filter(str.isalpha, entry["interval"]))
            return (unit_weight.get(unit, 1) * num, entry["time"].timestamp())
        except:
            return (0, entry["time"].timestamp())

    best_entry = sorted(valid_entries, key=interval_sort_key, reverse=True)[0]

    # RSI suodatin (ei muuta)
    if RSI_FILTER_ENABLED:
        try:
            ohlcv, _ = fetch_ohlcv_fallback(symbol, intervals=[RSI_FILTER_INTERVAL], limit=100)
            df_rsi = ohlcv.get(RSI_FILTER_INTERVAL)

            if df_rsi is None or df_rsi.empty:
                print(f"❌ RSI data puuttuu symbolilta {symbol} – signaali blokataan")
                return {}

            rsi_series = calculate_rsi(df_rsi, period=RSI_FILTER_PERIOD)
            latest_rsi = rsi_series.dropna().iloc[-1]

            if best_entry["signal"] == "buy" and latest_rsi > RSI_FILTER_BUY_MAX:
                return {}
            elif best_entry["signal"] == "sell" and latest_rsi < RSI_FILTER_SELL_MIN:
                return {}

        except Exception as e:
            print(f"⚠️ RSI-suodatus epäonnistui symbolille {symbol}: {e}")
            return {}

    return {
        "signal": best_entry["signal"],
        "interval": best_entry["interval"],
        "mode": best_entry["mode"]
    }
