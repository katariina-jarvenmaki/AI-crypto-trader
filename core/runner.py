# runner.py
from signals.divergence_detector import DivergenceDetector
from signals.rsi_analyzer import rsi_analyzer
from integrations.binance_api_client import fetch_ohlcv_for_intervals
import pandas as pd

def run_analysis_for_symbol(symbol, override_signal=None):
    
    print(f"\n🔍 Processing symbol: {symbol}")

    if override_signal:
        print(f"⚠️ Override signal activated for {symbol}")
        print(f"🚨 Final signal for {symbol}: {override_signal.upper()} (override)")
        return

    data_by_interval = fetch_ohlcv_for_intervals(symbol=symbol, intervals=["1h"], limit=100)
    df = data_by_interval.get("1h")

    if df is not None and not df.empty:
        # If 'timestamp' is the index, reset it to make it a column
        if df.index.name == 'timestamp':
            df = df.reset_index()

        detector = DivergenceDetector(df)
        divergence = detector.detect_all_divergences(symbol=symbol, interval="1h")
        if divergence:
            signal_type = "buy" if divergence["type"] == "bull" else "sell"
            strategy = divergence.get("strategy", "unknown")
            print(f"📈 {strategy.capitalize()} signal detected: {signal_type.upper()} (price: {divergence['price']}, time: {divergence['time']})")
            print(f"🚨 Final signal for {symbol}: {signal_type.upper()} ({strategy})")

    rsi_result = rsi_analyzer(symbol)
    rsi_signal = rsi_result.get("signal")
    rsi_value = rsi_result.get("rsi")
    rsi_interval = rsi_result.get("interval", "1h")
    strategy = rsi_result.get("strategy", "rsi")

    if rsi_signal in ["buy", "sell"]:
        print(f"📉 {strategy.upper()} signal detected for {symbol}: {rsi_signal.upper()} | Interval: {rsi_interval} | RSI: {rsi_value}")
        print(f"🚨 Final signal for {symbol}: {rsi_signal.upper()} ({strategy})")
    else:
        print(f"⚪ No RSI signal for {symbol} | Interval: {rsi_interval} | RSI: {rsi_value}")
