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
from integrations.bybit_api_client import client as bybit_client, set_stop_loss_and_trailing_stop, parse_percent
import pandas as pd
import json

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
        mode=mode,
        interval=interval
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

import json
import pandas as pd
from scripts.trade_order_logger import load_trade_logs, update_order_status
from scripts.sorting import sort_orders_by_stoploss_priority

def check_positions_and_update_logs(symbols_to_check, platform="ByBit"):
    try:
        if platform != "ByBit":
            print(f"[ERROR] Unsupported platform for this method: {platform}")
            return []

        if not symbols_to_check:
            print("[WARN] No symbols provided for open position check.")
            return []

        all_positions = []

        for symbol in symbols_to_check:
            bybit_symbol = symbol.replace("USDC", "USDT")
            try:
                response = bybit_client.get_positions(
                    category="linear",
                    symbol=bybit_symbol
                )
                if "result" in response and "list" in response["result"]:
                    for pos in response["result"]["list"]:
                        size = float(pos["size"])
                        if size > 0:
                            all_positions.append({
                                "symbol": pos.get("symbol", "unknown"),
                                "side": pos["side"],
                                "size": size
                            })
            except Exception as inner_e:
                print(f"[ERROR] Failed to fetch position for {bybit_symbol}: {inner_e}")
                continue

        try:
            with open("logs/order_log.json", "r") as f:
                order_data = json.load(f)

            side_mapping = {
                "long": "Buy",
                "short": "Sell"
            }

            updated_any = False  # 🆕 uusi lippu

            for sym_key, sides in order_data.items():
                for side_key, orders in sides.items():
                    for order in orders:
                        if order.get("status") != "complete":
                            order_symbol = sym_key.replace("USDC", "USDT")
                            expected_pos_side = side_mapping.get(side_key.lower())
                            match_found = any(
                                pos["symbol"] == order_symbol and pos["side"] == expected_pos_side
                                for pos in all_positions
                            )

                            if not match_found:
                                updated = update_order_status(order.get("timestamp"), "complete")
                                if updated:
                                    updated_any = True  # 🆕 merkitse että jotain on päivitetty
                                else:
                                    print(f"[WARN] Could not update status for {order.get('timestamp')}")

            if updated_any:
                print("\n✅ Marked some orders as complete.")
            else:
                print("\nℹ️  No order statuses needed updating.")

        except Exception as e:
            print(f"[ERROR] Failed to update order status logs: {e}")

        return all_positions

    except Exception as e:
        print(f"[ERROR] Failed to fetch positions: {e}")
        return []

def stop_loss_updater():
    import os
    import json
    from integrations.bybit_api_client import parse_percent
    from core.runner import bybit_client

    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "stoploss_config.json")
    config_path = os.path.abspath(config_path)

    try:
        with open(config_path, "r") as cf:
            config = json.load(cf)

        set_sl_percent = parse_percent(config.get("set_stoploss_percent", "0.16%"))
        partial_sl_percent = parse_percent(config.get("partial_stoploss_percent", "0.15%"))
        trailing_percent = parse_percent(config.get("trailing_stoploss_percent", "0.15%"))

        with open("logs/order_log.json", "r") as f:
            order_data = json.load(f)

        print("\n📈 Checking live prices for open orders...")

        for symbol_key, sides in order_data.items():
            bybit_symbol = symbol_key.replace("USDC", "USDT")

            for side_key, orders in sides.items():
                for order in orders:
                    if order.get("status") == "complete":
                        continue

                    try:
                        direction = side_key.lower()
                        entry_price = float(order.get("price"))

                        price_data = bybit_client.get_tickers(category="linear", symbol=bybit_symbol)
                        if "result" in price_data and "list" in price_data["result"]:
                            last_price = float(price_data["result"]["list"][0]["lastPrice"])
                        else:
                            print(f"[WARN] No price data found for {bybit_symbol}")
                            continue

                        if direction == "long":
                            target_price = entry_price * (1 + set_sl_percent)
                            condition_met = last_price > target_price
                            position_idx = 1
                        elif direction == "short":
                            target_price = entry_price * (1 - set_sl_percent)
                            condition_met = last_price < target_price
                            position_idx = 2
                        else:
                            print(f"[WARN] Unknown direction for {bybit_symbol}: {direction}")
                            continue

                        print(f"🔸 {symbol_key} | Dir: {direction.upper()} | Entry: {entry_price:.4f} | Target: {target_price:.4f} | Live: {last_price:.4f}")

                        if condition_met:
                            print(f"✅ Trigger condition met for {symbol_key} ({direction})")

                            sl_offset = entry_price * partial_sl_percent
                            if direction == "long":
                                partial_sl_price = entry_price + sl_offset
                            else:
                                partial_sl_price = entry_price - sl_offset

                            print(f"🔒 Setting partial SL to {partial_sl_price:.4f}")
                            print(f"📉 Setting trailing SL at {trailing_percent * 100:.2f}% (ignored in partial mode)")

                            try:
                                body = {
                                    "category": "linear",
                                    "symbol": bybit_symbol,
                                    "stopLoss": str(round(partial_sl_price, 4)),
                                    "slSize": "1",
                                    "slTriggerBy": "LastPrice",
                                    "tpslMode": "Partial",
                                    "positionIdx": position_idx
                                }

                                print(f"📤 Sending SL update: {body}")

                                response = bybit_client.set_trading_stop(**body)

                                print(f"🟢 SL updated: {response}")

                            except Exception as sl_err:
                                print(f"[ERROR] Failed to update stop loss: {sl_err}")

                        else:
                            print("⏳ Condition not yet met.")

                    except Exception as price_err:
                        print(f"[ERROR] Failed to get price for {bybit_symbol}: {price_err}")

    except Exception as e:
        print(f"[ERROR] Could not check open order prices: {e}")
