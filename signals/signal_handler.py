# signals/signal_handler.py
#
# 1. Checks override signal (highest priority)
# Defines disallowed signals
# 2. Checks Divergence signals
# 3. Checks RSI signals (lowest priority)
# Uses momentum to guide analysis
# 4. Checks log signal according to momentum
# Returns results
#
from signals.determine_momentum import determine_signal_with_momentum_and_volume
from signals.divergence_detector import DivergenceDetector
from signals.rsi_analyzer import rsi_analyzer
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback
import pandas as pd

from signals.log_based_signal import get_log_based_signal  # Muista importoida tämä

def get_signal(symbol: str, interval: str, is_first_run: bool = False, override_signal: str = None, long_only: bool = False, short_only: bool = False) -> dict:

    signal_info = {"signal": None, "mode": None, "interval": None}

    # 1. Override signal (highest priority)
    if override_signal and is_first_run:
        if long_only and override_signal == "sell":
            print(f"❌ Override signal '{override_signal}' blocked by long-only mode.")
            return {}
        if short_only and override_signal == "buy":
            print(f"❌ Override signal '{override_signal}' blocked by short-only mode.")
            return {}
        return {"signal": override_signal, "mode": "override"}

    # Define disallowed signal
    if long_only:
        disallowed = "sell"
    elif short_only:
        disallowed = "buy"
    else:
        disallowed = None

    # 2. Divergence check
    data_by_interval, _ = fetch_ohlcv_fallback(symbol=symbol, intervals=["1h"], limit=100)
    df = data_by_interval.get("1h")
    if df is None or df.empty:
        print(f"Skipping signal analysis for {symbol} on {interval}: No data available.")
        return {}

    if df.index.name == 'timestamp':
        df = df.reset_index()

    detector = DivergenceDetector(df)
    divergence = detector.detect_all_divergences(symbol=symbol, interval=interval)
    if divergence:
        signal_type = "buy" if divergence["type"] == "bull" else "sell"
        if disallowed == signal_type:
            print(f"❌ Divergence signal '{signal_type}' blocked by {'long-only' if long_only else 'short-only'} mode.")
            return {}
        print(f"📢 Divergence signal detected.")
        return {"signal": signal_type, "mode": divergence.get("mode", "divergence"), "interval": interval}

    # 3. RSI signal
    rsi_result = rsi_analyzer(symbol)
    rsi_signal = rsi_result.get("signal")
    if rsi_signal in ["buy", "sell"]:
        if disallowed == rsi_signal:
            print(f"❌ RSI signal '{rsi_signal}' blocked by {'long-only' if long_only else 'short-only'} mode.")
            return {}
        return {
            "signal": rsi_signal,
            "mode": rsi_result.get("mode", "rsi"),
            "interval": rsi_result.get("interval", interval),
            "rsi": rsi_result.get("rsi")
        }

    # Momentum guide analysis (non-overriding)
    ohlcv_data, _ = fetch_ohlcv_fallback(symbol, intervals=["5m"], limit=30)
    suggested_signal = None

    if ohlcv_data and "5m" in ohlcv_data and not ohlcv_data["5m"].empty:
        df_5m = ohlcv_data["5m"]
        momentum_result = determine_signal_with_momentum_and_volume(df_5m, symbol, intervals=[5])

        suggested_signal = momentum_result.get("suggested_signal")
        signal_info["momentum_guide"] = {
            "suggested_signal": suggested_signal,
            "strength": momentum_result.get("momentum_strength"),
            "interpretation": momentum_result.get("interpretation"),
            "volume_multiplier": momentum_result.get("volume_multiplier")
        }

        if momentum_result.get("momentum_strength") in ["strong", "weak"]:
            print(f"📈 Momentum guide suggests {suggested_signal.upper()} ({momentum_result.get('momentum_strength')})")

    # 4. Log-based signal if suggested_signal exists
    if suggested_signal in ["buy", "sell"]:
        log_signal = get_log_based_signal(symbol)

        # Find the highest-priority log signal that is not "complete"
        highest_bias = None
        hierarchy = ["1w", "1d", "4h", "2h", "1h", "30m", "15m", "5m", "3m", "1m"]

        if log_signal:
            for tf in hierarchy:
                if tf in log_signal:
                    for side in ["buy", "sell"]:
                        entry = log_signal[tf].get(side)
                        if entry and entry.get("status") != "complete":
                            highest_bias = {"interval": tf, "signal": side}
                            break
                if highest_bias:
                    break

        # Block signal if momentum contradicts long-term log bias
        if highest_bias:
            bias_dir = highest_bias["signal"]
            if suggested_signal != bias_dir:
                print(f"⛔ Momentum {suggested_signal.upper()} contradicts long-term log bias {bias_dir.upper()} ({highest_bias['interval']})")
                return {}

        # Block if long-only/short-only restriction is active
        if disallowed == suggested_signal:
            print(f"❌ Log-filtered momentum '{suggested_signal}' blocked by {'long-only' if long_only else 'short-only'} mode.")
            return {}

        # ✅ Accept signal
        if highest_bias:
            bias_info = f"{highest_bias['signal'].upper()} bias from {highest_bias['interval']}"
            print(f"✅ Momentum signal {suggested_signal.upper()} confirmed by log – {bias_info}")
        else:
            print(f"ℹ️ No active log bias found – accepting momentum signal {suggested_signal.upper()} without log confirmation")

        result = {
            "signal": suggested_signal,
            "mode": "log" if highest_bias else "momentum",
            "interval": highest_bias["interval"] if highest_bias else interval,
            "log_bias_interval": highest_bias["interval"] if highest_bias else None
        }
        return result

    print(f"⚪ No signal for {symbol}")
    return {}