from datetime import datetime
import pytz 
from pytz import timezone
from market.market_handler import get_market_state
from configs.config import TIMEZONE
from signals.signal_handler import get_signal
from scripts.signal_limiter import is_signal_allowed, update_signal_log
import pandas as pd

def run_analysis_for_symbol(symbol, is_first_run, override_signal=None):
    print(f"\n🔍 Processing symbol: {symbol}")

    # Get the signals for the symbols
    signal_info = get_signal(symbol=symbol, interval=None, is_first_run=is_first_run, override_signal=override_signal)
    final_signal = signal_info.get("signal")
    mode = signal_info.get("mode")
    interval = signal_info.get("interval")

    # ✅ Jatka vain jos signaali on 'buy' tai 'sell'
    if final_signal not in ("buy", "sell"):
        print("⚪ No actionable signal")
        return

    # Get market state
    market_info = get_market_state(symbol=symbol)

    now = datetime.now(pytz.timezone(TIMEZONE.zone))
    update_signal_log(
        symbol=symbol,
        interval=interval,
        signal_type=final_signal,
        now=now,
        mode=mode,
        market_info=market_info
    )
