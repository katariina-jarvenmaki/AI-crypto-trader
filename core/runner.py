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
from scripts.min_buy_calc import calculate_minimum_valid_purchase
from scripts.spot_order_handler import place_spot_trade_with_tp_sl

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

    # Continue only, if a signal 'buy' or 'sell'
    if final_signal not in ("buy", "sell"):
        return

    # Get market state info
    market_info = get_market_state(symbol=symbol)
    market_state = market_info.get("state")
    started_on = market_info.get("started_on")

    # Check riskmanagement
    status = None
    if override_signal:
        risk_strength = "strong"
    else:
        risk_strength = check_riskmanagement(symbol=symbol, signal=final_signal)
        if risk_strength == "strong":
            status = "complete"

    # Strategy handler
    if risk_strength == "strong":
        strategy_handler = StrategyHandler()
        strategy_plan = strategy_handler.determine_strategy(
            market_state=market_state,
            signal=final_signal,
            mode=mode,
            interval=interval
        )
        print(f"📌 Strategy: {strategy_plan['selected_strategies']} in {strategy_plan['market_strategy']}. Market state: {market_state}, started on: {started_on}")

    # Only log if signal strength is "strong" or "weak"
    if risk_strength in ("strong", "weak"):
        if (mode == "log" and status == "complete") or (mode not in ("log", "override")):
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
    if risk_strength == "strong":
        if mode == "override":
            print(f"⚠️  Override signal activated for {symbol}: {override_signal.upper()}")
        elif mode == "divergence":
            print(f"📈 {mode.upper()} signal detected for {symbol}: {final_signal.upper()}")
        elif mode == "rsi":
            print(f"📉 {mode.upper()} signal detected for {symbol}: {final_signal.upper()} | Interval: {interval} | RSI: {rsi}")
        elif mode == "log":
            print(f"📝 Log-based signal detected for {symbol}: {final_signal.upper()} | Interval: {interval}")

    # Calculate the price
    if risk_strength == "strong" and final_signal == "buy":
        result = calculate_minimum_valid_purchase(symbol)

        # Laske osto ja tee kaupat
        if result:
            print(f"✅ Minimiosto laskettu {symbol}: {result['qty']} kpl @ {result['price']:.4f} → yhteensä {result['cost']:.2f} USD")
            
            order_result = place_spot_trade_with_tp_sl(
                symbol=symbol,
                qty=result["qty"],
                entry_price=result["price"],
                tick_size=result["step_size"]
            )

            if order_result:
                print(f"✅ Kauppa suoritettu ja TP/SL asetettu: TP @ {order_result['tp_price']}, SL @ {order_result['sl_price']}")
            else:
                print(f"❌ Kaupan suoritus epäonnistui symbolille {symbol}")

        else:
            print("❌ Minimioston laskenta epäonnistui.")