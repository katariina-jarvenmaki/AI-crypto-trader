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

from datetime import datetime
import pytz 
from pytz import timezone
from market.market_handler import get_market_state
from configs.config import TIMEZONE
from signals.signal_handler import get_signal
from scripts.signal_limiter import is_signal_allowed, update_signal_log
from scripts.order_limiter import can_initiate
from riskmanagement.riskmanagement_handler import check_riskmanagement
from strategy.strategy_handler import StrategyHandler
from trade.execute_binance_long import execute_binance_long
from trade.execute_bybit_long import execute_bybit_long
from trade.execute_bybit_short import execute_bybit_short
from scripts.trade_order_logger import log_trade
import pandas as pd

# Symbol processing loop
def run_analysis_for_symbol(selected_symbols, symbol, is_first_run, initiated_counts, override_signal=None, volume_mode=None, long_only=False, short_only=False):

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

    # Continue only, if a signal 'buy' or 'sell'
    if final_signal not in ("buy", "sell"):
        return

    # Check the order counts
    direction = None
    if final_signal == "buy": direction = "long"
    elif final_signal == "sell": direction = "short"
    # Check if we're allowed to initiate based on fairness logic
    if direction and not can_initiate(symbol, direction, initiated_counts, all_symbols=selected_symbols):
        print(f"⛔ Skipping {symbol} {direction}: too many initiations compared to others.")
        return

    # Get market state info
    market_info = get_market_state(symbol=symbol)
    market_state = market_info.get("state")
    started_on = market_info.get("started_on")
    print(f"📊 Market state: {market_state}, started on: {started_on}")

    # Check riskmanagement
    status = "unused"
    risk_strength, price_changes, volume_multiplier, reverse_result = check_riskmanagement(
        symbol=symbol,
        signal=final_signal,
        market_state=market_state,
        override_signal=(mode in ["override", "divergence"]),
        mode=mode
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

    # Do the signal logging
    selected_change_text = str(price_changes) if price_changes else "n/a"
    if risk_strength in ("strong", "weak", "none") and (
        mode not in ("momentum", "log", "override") or ((mode == "log" or mode == "momentum") and status == "complete")
    ):
        now = datetime.now(pytz.timezone(TIMEZONE.zone))
        update_signal_log(
            symbol=symbol,
            interval=interval,
            signal_type=final_signal,
            mode=mode,
            now=now,
            status=status,
            momentum_strength=risk_strength,
            reverse_signal_info=reverse_result,
            volume_multiplier=volume_multiplier,
            price_change=selected_change_text,
            market_state=market_state,
            started_on=started_on
        )

    # Continue only, if a risk_strength is strong AND reverse signal is not strong
    reverse_strength = reverse_result.get("momentum_strength", "n/a")

    # Special case: allow BUY in neutral_sideways if reverse is not strong
    if (
        final_signal == "buy"
        and market_state == "neutral_sideways"
        and reverse_strength != "strong"
    ):
        print("✅ BUY allowed in neutral_sideways due to weak reverse signal.")
    else:
        if risk_strength != "strong" or reverse_strength == "strong":
            if risk_strength == "strong":
                print(f"❌ Signal {final_signal.upper()} blocked due to strong reverse signal.")
            return

    # Print results
    if mode == "override":
        print(f"🔔 Starting strategies for Overide signal for {symbol}: {override_signal.upper()}")
    elif mode == "divergence":
        print(f"🔔 Starting strategies for {mode} signal for {symbol}: {final_signal.upper()}")
    elif mode == "rsi":
        print(f"🔔 Starting strategies for {mode} signal for {symbol}: {final_signal.upper()} | Interval: {interval} | RSI: {rsi}")
    elif mode == "log":
        print(f"🔔 Starting strategies for {mode} signal for {symbol}: {final_signal.upper()} | Interval: {interval}")

    #***** STRATEGIES *****#

    # print(f"Add strategy logic here...")

    #***** LONGS *****#

    if final_signal == "buy":

        # Binance
        binance_result = execute_binance_long(symbol, risk_strength)
        if binance_result:
            log_trade(
                symbol=binance_result["symbol"],
                platform="Binance",
                direction="long",
                qty=binance_result["qty"],
                price=binance_result["price"],
                leverage=binance_result["leverage"],
                order_take_profit=binance_result["tp_price"],
                order_stop_loss=binance_result["sl_price"],
                interval=interval,
                mode=mode,
                market_state=market_state,
                started_on=started_on,
                momentum_strength=risk_strength,
                price_change=selected_change_text,
                volume_multiplier=volume_multiplier,
                reverse_signal_info=reverse_result
            )

        # Bybit
        bybit_result = execute_bybit_long(symbol, risk_strength)
        if bybit_result:
            log_trade(
                symbol=bybit_result["symbol"],
                platform="ByBit",
                direction="long",
                qty=bybit_result["qty"],
                price=bybit_result["price"],
                cost=bybit_result["cost"],
                leverage=bybit_result["leverage"],
                order_take_profit=bybit_result["tp_price"],
                order_stop_loss=bybit_result["sl_price"],
                interval=interval,
                mode=mode,
                market_state=market_state,
                started_on=started_on,
                momentum_strength=risk_strength,
                price_change=selected_change_text,
                volume_multiplier=volume_multiplier,
                reverse_signal_info=reverse_result
            )

    #***** SHORTS *****#

    if final_signal == "sell":

        # Bybit
        bybit_result = execute_bybit_short(symbol, risk_strength)
        if bybit_result:
            log_trade(
                symbol=bybit_result["symbol"],
                platform="ByBit",
                direction="short",
                qty=bybit_result["qty"],
                price=bybit_result["price"],
                cost=bybit_result["cost"],
                leverage=bybit_result["leverage"],
                order_take_profit=bybit_result["tp_price"],
                order_stop_loss=bybit_result["sl_price"],
                interval=interval,
                mode=mode,
                market_state=market_state,
                started_on=started_on,
                momentum_strength=risk_strength,
                price_change=selected_change_text,
                volume_multiplier=volume_multiplier,
                reverse_signal_info=reverse_result
            )

    #***** STOP LOSSES *****#