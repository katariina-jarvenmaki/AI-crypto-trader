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

def get_signal(symbol: str, interval: str, is_first_run: bool = False, override_signal: str = None) -> dict:
    """
    Determines the final signal based on a hierarchy: override, divergence, then RSI.

    Args:
        symbol (str): The trading pair symbol (e.g., "BTCUSDT").
        interval (str): The candlestick interval (e.g., "1h").
        is_first_run (bool): True if this is the first analysis run, useful for override signal.
        override_signal (str): An optional override signal ("buy" or "sell").

    Returns:
        dict: A dictionary containing 'signal', 'mode', and 'interval'.
              Returns an empty dictionary if no signal is found.
    """
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

    # 3. Check for RSI signal (lowest priority)
    rsi_result = rsi_analyzer(symbol)
    rsi_signal = rsi_result.get("signal")
    rsi_value = rsi_result.get("rsi")
    rsi_interval = rsi_result.get("interval", interval)

    # Collect values to return
    if rsi_signal in ["buy", "sell"]:
        mode = rsi_result.get("mode", "rsi")
        signal_info["signal"] = rsi_signal
        signal_info["mode"] = mode
        signal_info["interval"] = rsi_interval
        signal_info["rsi"] = rsi_value
        return signal_info
    else:
        print(f"⚪ No RSI signal for {symbol} | Interval: {rsi_interval} | RSI: {rsi_value}")

    return {} 