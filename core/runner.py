# core/runner.py
#
# 1. Get raw signals
# 2. Do market analyzes
# 3. Riskmanagement
# 4. Strategy selection
# 5. Calculate minium price
# 6. Make a long order with 1%tp and 10%sl
# 7. Selling in loop?
# 8. Updating stop losses
#
from datetime import datetime
import pytz 
from pytz import timezone
from market.market_handler import get_market_state
from configs.config import TIMEZONE
from signals.signal_handler import get_signal
from scripts.signal_limiter import is_signal_allowed, update_signal_log
from riskmanagement.riskmanagement_handler import check_riskmanagement
from strategy.strategy_handler import StrategyHandler
from trade.execute_binance_long import execute_binance_long
from trade.execute_bybit_long import execute_bybit_long
from trade.execute_bybit_short import execute_bybit_short
from scripts.trade_order_logger import log_trade

import pandas as pd

# Symbol processing loop
def run_analysis_for_symbol(symbol, is_first_run, override_signal=None, volume_mode=None, long_only=False, short_only=False):

    print(f"\n🔍 Processing symbol: {symbol}")

    # Get the signals for the symbols
    signal_info = get_signal(
        symbol=symbol,
        interval=None,
        is_first_run=is_first_run,
        override_signal=override_signal,
        long_only=long_only,
        short_only=short_only
    )
    final_signal = signal_info.get("signal")
    mode = signal_info.get("mode")
    interval = signal_info.get("interval")
    rsi = signal_info.get("rsi")
    print(f"Signal: {final_signal }")
    print(f"Mode: {mode}")
    print(f"Interval: {interval}")
    print(f"RSI: {rsi}")

    # Continue only, if a signal 'buy' or 'sell'
    if final_signal not in ("buy", "sell"):
        return

    # Get market state info
    market_info = get_market_state(symbol=symbol)
    market_state = market_info.get("state")
    started_on = market_info.get("started_on")
    print(f"📊 Market state: {market_state}, started on: {started_on}")

    # Check riskmanagement
    status = None
    risk_strength, price_changes, volume_multiplier = check_riskmanagement(
        symbol=symbol,
        signal=final_signal,
        market_state=market_state,
        override_signal=(mode in ["override", "divergence"])
    )
    if risk_strength == "strong":
        status = "complete"

    # Strategy handler
    # 4. Determine strategy
    strategy_plan = None
    if risk_strength == "strong":
        strategy_handler = StrategyHandler()
        strategy_plan = strategy_handler.determine_strategy(
            market_state=market_state,
            signal=final_signal,
            mode=mode,
            interval=interval
        )
        if strategy_plan:
            print(f"📌 Strategy: {strategy_plan['selected_strategies']}")

    # Do the logging
    selected_change_text = str(price_changes) if price_changes else "n/a"
    if risk_strength in ("strong", "weak", "none") and mode not in ("log", "override"):
        now = datetime.now(pytz.timezone(TIMEZONE.zone))
        print(f"Interval: {interval}")
        print(f"Now: {now}")
        print(f"Mode: {mode}")
        print(f"Market state: {market_state}")
        print(f"Started on: {started_on}")
        print(f"Momemntum Strength: {risk_strength}")
        print(f"Status: {status}")
        print(f"Price Change: {selected_change_text}")
        print(f"Volume Multiplier: {volume_multiplier}")
        update_signal_log(
            symbol=symbol,
            interval=interval,
            signal_type=final_signal,
            now=now,
            mode=mode,
            market_state=market_state,
            started_on=started_on,
            momentum_strength=risk_strength,
            status=status,
            price_change=selected_change_text,
            volume_multiplier=volume_multiplier 
        )
    if risk_strength in ("strong", "weak"):
        if (mode == "log" and status == "complete") or (mode not in ("log", "override")):
            now = datetime.now(pytz.timezone(TIMEZONE.zone))
            print(f"Interval: {interval}")
            print(f"Now: {now}")
            print(f"Mode: {mode}")
            print(f"Market state: {market_state}")
            print(f"Started on: {started_on}")
            print(f"Momemntum Strength: {risk_strength}")
            print(f"Status: {status}")
            print(f"Price Change: {selected_change_text}")
            print(f"Volume Multiplier: {volume_multiplier}")
            update_signal_log(
                symbol=symbol,
                interval=interval,
                signal_type=final_signal,
                now=now,
                mode=mode,
                market_state=market_state,
                started_on=started_on,
                momentum_strength=risk_strength,
                status=status,
                price_change=selected_change_text,
                volume_multiplier=volume_multiplier 
            )

    # Continue only, if a risk_strength is strong
    if risk_strength != "strong":
        return

    # Print results
    if mode == "override":
        print(f"🔔 Starting strategies for Overide signal for {symbol}: {override_signal.upper()}")
    elif mode == "divergence":
        print(f"🔔 Starting strategies for {mode.upper()} signal for {symbol}: {final_signal.upper()}")
    elif mode == "rsi":
        print(f"🔔 Starting strategies for {mode.upper()} signal for {symbol}: {final_signal.upper()} | Interval: {interval} | RSI: {rsi}")
    elif mode == "log":
        print(f"🔔 Starting strategies for {mode.upper()} signal for {symbol}: {final_signal.upper()} | Interval: {interval}")

    #***** STRATEGIES *****#

    print(f"Add strategy logic here...")

    #***** BUYING *****#

    if final_signal == "buy":

        # Binance
        binance_result = execute_binance_long(symbol, risk_strength)
        if binance_result:
            log_trade(**binance_result)

        # Bybit
        bybit_result = execute_bybit_long(symbol, risk_strength)
        if bybit_result:
            log_trade(**bybit_result)

    #***** SELLING *****#

    if final_signal == "sell":

        # Bybit
        bybit_result = execute_bybit_short(symbol, risk_strength)
        if bybit_result:
            log_trade(**bybit_result)

    #***** STOP LOSSES *****#
