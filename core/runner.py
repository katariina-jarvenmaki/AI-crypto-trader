# core/runner.py
#
# 1. Get raw signals
# 2. Do market analyzes
# 3. Riskmanagement
# 4. Strategy selection
# 5. Run the strategies
# 6. Returns results
#
from datetime import datetime
import pytz 
from pytz import timezone
from market.market_handler import get_market_state
from configs.config import TIMEZONE
from signals.signal_handler import get_signal
from scripts.signal_limiter import is_signal_allowed, update_signal_log
from riskmanagement.riskmanagement_handler import check_riskmanagement
import pandas as pd

# Symbol processing loop
def run_analysis_for_symbol(symbol, is_first_run, override_signal=None, volume_mode=None):
    print(f"\n🔍 Processing symbol: {symbol}")

    # Get the signals for the symbols
    signal_info = get_signal(symbol=symbol, interval=None, is_first_run=is_first_run, override_signal=override_signal)
    final_signal = signal_info.get("signal")
    mode = signal_info.get("mode")
    interval = signal_info.get("interval")
    rsi = signal_info.get("rsi")

    # Continue only, if a signal 'buy' or 'sell'
    if final_signal not in ("buy", "sell"):
        return

    # Get market state info
    market_info = get_market_state(symbol=symbol)
    market_state = market_info.get("state")
    started_on = market_info.get("started_on")

    # Check riskmanagement
    status = None
    risk_strength = check_riskmanagement(symbol=symbol, signal=final_signal)
    if risk_strength == "strong":
        status = "complete"

    # Only log if signal strength is "strong" or "weak"
    if risk_strength in ("strong", "weak"):
        now = datetime.now(pytz.timezone(TIMEZONE.zone))
        update_signal_log(
            symbol=symbol,
            interval=interval,
            signal_type=final_signal,
            now=now,
            mode=mode,
            market_state=market_state,
            started_on=started_on,
            momentum_strength=risk_strength,
            status=status
        )

    # Print results
    if mode == "override":
        print(f"⚠️  Override signal activated for {symbol}: {override_signal.upper()}")
    elif mode == "divergence":
        print(f"📈 {mode.upper()} signal detected for {symbol}: {final_signal.upper()}")
    elif mode == "rsi":
        print(f"📉 {mode.upper()} signal detected for {symbol}: {final_signal.upper()} | Interval: {interval} | RSI: {rsi}")
    