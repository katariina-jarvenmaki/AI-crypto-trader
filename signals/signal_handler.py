# signals/signal_handler.py

from signals.divergence_detector import DivergenceDetector
from signals.rsi_analyzer import rsi_analyzer
from signals.momentum_signal import get_momentum_signal, determine_signal_with_momentum_and_volume
from signals.log_signal import get_log_signal
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback

def get_signal(symbol: str, interval: str, is_first_run: bool = False, override_signal: str = None, long_only: bool = False, short_only: bool = False) -> dict:

    # 1. Override signal (highest priority)
    if override_signal and is_first_run:
        if long_only and override_signal == "sell":
            print(f"❌ Override signal '{override_signal}' blocked by long-only mode.")
            return {}
        if short_only and override_signal == "buy":
            print(f"❌ Override signal '{override_signal}' blocked by short-only mode.")
            return {}
        return {"signal": override_signal, "mode": "override"}

    # Määritä mikä signaali on estetty
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

    # 4. Logipohjainen signaali (ennen momentumia)
    ohlcv_data, _ = fetch_ohlcv_fallback(symbol, intervals=["5m"], limit=100)
    df_5m = ohlcv_data.get("5m")

    if df_5m is None or df_5m.empty:
        print(f"❌ Missing 5m OHLCV data for {symbol}")
        return None

    momentum_result = determine_signal_with_momentum_and_volume(df_5m, symbol, intervals=[5])
    suggested_signal = momentum_result.get("suggested_signal")
    if suggested_signal:
        print(f"📊 Momentum guide suggests: {suggested_signal}")

    log_result = get_log_signal(symbol, signal_type=suggested_signal)
    if log_result:
        raw_signal = log_result["signal"]
        if (long_only and raw_signal == "sell") or (short_only and raw_signal == "buy"):
            print(f"❌ Log signal '{raw_signal}' blocked by mode.")
        else:
            print(f"✅ Using log-based signal: {raw_signal}")
            return {
                "signal": raw_signal,
                "mode": log_result.get("mode", "log"),
                "interval": log_result["interval"],
                "log_bias_interval": log_result["interval"]
            }

    # 5. Momentum-signaali (jos log ei palauttanut mitään)
    momentum_result = get_momentum_signal(symbol)
    if momentum_result:
        signal_data, momentum_info = momentum_result

        # momentum_info on metadata, signal_data on esim: {"signal": "buy", "interval": "5m"}
        if signal_data and "signal" in signal_data:
            signal_value = signal_data["signal"]
            if (long_only and signal_value == "sell") or (short_only and signal_value == "buy"):
                print(f"❌ Momentum signal '{signal_value}' blocked by mode.")
            else:
                print(f"✅ Using filtered momentum signal: {signal_value}")
                return {
                    "signal": signal_value,
                    "mode": "momentum",
                    "interval": signal_data.get("interval"),
                    "log_bias_interval": None
                }

    print(f"⚪ No signal for {symbol}")
    return {}