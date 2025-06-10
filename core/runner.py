# runner.py
from signals.signal_handler import get_signal
import pandas as pd # pandas is kept here in case other parts of runner.py use it

def run_analysis_for_symbol(symbol, is_first_run, override_signal=None):

    print(f"\n🔍 Processing symbol: {symbol}")

    # Get the signals for the symbols
    signal_info = get_signal(symbol=symbol, interval=None, is_first_run=is_first_run, override_signal=override_signal)
    final_signal = signal_info.get("signal")
    mode = signal_info.get("mode")
    interval = signal_info.get("interval")
