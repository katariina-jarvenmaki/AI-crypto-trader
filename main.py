# main.py
import pandas as pd
import sys
import time
from scripts.platform_selection import get_selected_platform
from scripts.symbol_selection import get_selected_symbols
from scripts.binance_api_client import fetch_multi_ohlcv, fetch_ohlcv_for_intervals, get_all_current_prices
from scripts.divergence_detector import DivergenceDetector
from scripts.rsi_analyzer import rsi_analyzer
from configs.config import TIMEZONE
import pytz

arg_list = sys.argv[1:]  # Komentoriviparametrit ilman tiedostonimeä

# 1. Platformin valinta
try:
    selected_platform = get_selected_platform(arg_list)
except ValueError as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

# 2. Symbolit ilman platform-parametria
symbol_args = arg_list[1:] if selected_platform.lower() == arg_list[0].lower() else arg_list

# 3. Symbolien valinta
try:
    selected_symbols = get_selected_symbols(selected_platform, symbol_args)
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

override_signal = None
valid_signals = ["buy", "sell"]

if len(arg_list) >= 2 and arg_list[-1].lower() in valid_signals:
    override_signal = arg_list[-1].lower()
    print(f"⚠️ Override signal provided: {override_signal}")

# 🔁 Toistetaan 5 minuutin välein
while True:
    now = pd.Timestamp.utcnow().replace(tzinfo=pytz.utc).astimezone(TIMEZONE)
    print(f"\n🕒 Starting signal analysis loop {now:%Y-%m-%d %H:%M:%S %Z}")

    # 4. Tulostus
    print(f"✅ Selected platform: {selected_platform}")
    print(f"✅ Selected symbols: {selected_symbols}")

    for i, symbol in enumerate(selected_symbols):
        print(f"\n🔍 Processing symbol: {symbol}")

        if override_signal and i == 0:
            signal = override_signal
            strategy = "override"
            print(f"⚠️ Override signal activated for {symbol}")
            print(f"🚨 Final signal for {symbol}: {signal.upper()} ({strategy})")
            continue

        data_by_interval = fetch_ohlcv_for_intervals(symbol=symbol, intervals=["1h"], limit=100)
        df = data_by_interval.get("1h")
        divergence_signal = None

        if df is not None and not df.empty:
            if 'open_time' in df.columns:
                df = df.rename(columns={'open_time': 'timestamp'})
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)

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
        rsi_interval = rsi_result.get("interval", "1h")  # default, jos funktio ei palauta

        if rsi_signal in valid_signals:
            strategy = rsi_result.get("strategy", "rsi")
            print(f"📉 {strategy.upper()} signal detected for {symbol}: {rsi_signal.upper()} | Interval: {rsi_interval} | RSI: {rsi_value}")
            print(f"🚨 Final signal for {symbol}: {rsi_signal.upper()} ({strategy})")
        else:
            print(f"⚪ No RSI signal for {symbol} | Interval: {rsi_interval} | RSI: {rsi_value}")

    print("🕒 Sleeping for 5 minutes...\n")
    time.sleep(300)
