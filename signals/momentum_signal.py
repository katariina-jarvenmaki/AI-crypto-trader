# signals/momentum_signal.py

from signals.determine_momentum import determine_signal_with_momentum_and_volume
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback
from signals.log_signal import get_log_signal
from configs.config import (
    RSI_FILTER_ENABLED,
    RSI_FILTER_PERIOD,
    RSI_FILTER_BUY_MAX,
    RSI_FILTER_SELL_MIN
)
import pandas as pd

def get_momentum_signal(symbol: str):
    ohlcv_data, _ = fetch_ohlcv_fallback(symbol, intervals=["5m", "1h"], limit=100)
    if not ohlcv_data or "5m" not in ohlcv_data or "1h" not in ohlcv_data:
        return None, None

    df_5m = ohlcv_data["5m"]
    df_1h = ohlcv_data["1h"]

    if df_5m.empty or df_1h.empty:
        return None, None

    momentum_result = determine_signal_with_momentum_and_volume(df_5m, symbol, intervals=[5])
    suggested_signal = momentum_result.get("suggested_signal")

    momentum_info = {
        "suggested_signal": suggested_signal,
        "strength": momentum_result.get("momentum_strength"),
        "interpretation": momentum_result.get("interpretation"),
        "volume_multiplier": momentum_result.get("volume_multiplier")
    }

    if suggested_signal not in ["buy", "sell"]:
        return None, momentum_info

    # ⚠️ Estetään momentum-signaali jos kesken oleva sama signaali löytyy logista
    log_result = get_log_signal(symbol)
    if log_result and log_result.get("signal") == suggested_signal and log_result.get("status") != "complete":
        print(f"⚠️ Skipping momentum signal '{suggested_signal}' because matching unused log signal exists.")
        return None, momentum_info

    # RSI-suodatus (1h) konfiguraation mukaan
    if RSI_FILTER_ENABLED:
        try:
            close_1h = df_1h["close"]
            delta = close_1h.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=RSI_FILTER_PERIOD).mean()
            avg_loss = loss.rolling(window=RSI_FILTER_PERIOD).mean()
            rs = avg_gain / avg_loss
            rsi_1h = 100 - (100 / (1 + rs))
            rsi_latest = rsi_1h.dropna().iloc[-1]

            if suggested_signal == "buy" and rsi_latest > RSI_FILTER_BUY_MAX:
                print(f"❌ RSI-filter denied a buy-signal (RSI={rsi_latest:.2f} > {RSI_FILTER_BUY_MAX})")
                return None, momentum_info
            elif suggested_signal == "sell" and rsi_latest < RSI_FILTER_SELL_MIN:
                print(f"❌ RSI-filter denied a sell-signal (RSI={rsi_latest:.2f} < {RSI_FILTER_SELL_MIN})")
                return None, momentum_info
        except Exception as e:
            print(f"⚠️ RSI-suodatus epäonnistui: {e}")

    # SMA-suodatus (5m)
    sma_5m = df_5m["close"].rolling(window=50).mean().iloc[-1]
    price_now = df_5m["close"].iloc[-1]
    deviation_pct = (price_now - sma_5m) / sma_5m * 100

    if suggested_signal == "buy" and deviation_pct > 3:
        return None, momentum_info
    elif suggested_signal == "sell" and deviation_pct < -3:
        return None, momentum_info

    return {"signal": suggested_signal, "interval": "5m"}, momentum_info
