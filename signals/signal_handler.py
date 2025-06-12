# signal_handler.py
#
# 1. Checks override signal (highest priority)
# 2. Checks Divergence signals
# 3. Checks RSI signals (lowest priority)
# 6. Returns results
#
from signals.divergence_detector import DivergenceDetector
from signals.rsi_analyzer import rsi_analyzer
from integrations.binance_api_client import fetch_ohlcv_for_intervals
import pandas as pd

from signals.log_based_signal import get_log_based_signal  # Muista importoida tämä

def get_signal(symbol: str, interval: str, is_first_run: bool = False, override_signal: str = None) -> dict:

    signal_info = {"signal": None, "mode": None, "interval": None}

    # 1. Check for override signal (highest priority)
    if override_signal and is_first_run:
        signal_info["signal"] = override_signal
        signal_info["mode"] = "override"
        return signal_info

    # Fetch data for divergence and RSI analysis
    data_by_interval = fetch_ohlcv_for_intervals(symbol=symbol, intervals=["1h"], limit=100)
    df = data_by_interval.get("1h")
    if df is None or df.empty:
        print(f"Skipping signal analysis for {symbol} on {interval}: No data available.")
        return {}

    # Ensure timestamp is not an index for DivergenceDetector
    if df.index.name == 'timestamp':
        df = df.reset_index()

    # 2. Check for divergence signal
    detector = DivergenceDetector(df)
    divergence = detector.detect_all_divergences(symbol=symbol, interval=interval)
    if divergence:
        signal_type = "buy" if divergence["type"] == "bull" else "sell"
        mode = divergence.get("mode", "divergence")
        signal_info["signal"] = signal_type
        signal_info["mode"] = mode
        return signal_info

    # 3. Check for RSI signal
    rsi_result = rsi_analyzer(symbol)
    rsi_signal = rsi_result.get("signal")
    rsi_value = rsi_result.get("rsi")
    rsi_interval = rsi_result.get("interval", interval)

    if rsi_signal in ["buy", "sell"]:
        signal_info["signal"] = rsi_signal
        signal_info["mode"] = rsi_result.get("mode", "rsi")
        signal_info["interval"] = rsi_interval
        signal_info["rsi"] = rsi_value
        return signal_info

    # 4. Log-based signal (lowest priority)
    log_signal = get_log_based_signal(symbol)
    if log_signal and log_signal.get("signal") in ["buy", "sell"]:
        return log_signal

    return {}
