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
from scripts.process_stop_loss_logic import process_stop_loss_logic
from riskmanagement.riskmanagement_handler import check_riskmanagement
from strategy.strategy_handler import StrategyHandler
from trade.execute_binance_long import execute_binance_long
from trade.execute_bybit_long import execute_bybit_long
from trade.execute_bybit_short import execute_bybit_short
from scripts.trade_order_logger import log_trade
from scripts.filter_initiated_orders import filter_initiated_orders
from integrations.bybit_api_client import client as bybit_client, set_stop_loss_and_trailing_stop, parse_percent, get_bybit_symbol_info
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
        status = "completed"

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
        mode not in ("momentum", "log", "override") or ((mode == "log" or mode == "momentum") and status == "completed")
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
from scripts.trade_order_logger import load_trade_logs, update_order_status, safe_load_json
from scripts.sorting import sort_orders_by_stoploss_priority
import traceback

def check_positions_and_update_logs(symbols_to_check, platform="ByBit"):

    print(f"\n🔍 Doing position checks and log updates...")

    try:
        if platform != "ByBit":
            print(f"[ERROR] Unsupported platform for this method: {platform}")
            return []

        if not symbols_to_check:
            print("[WARN] No symbols provided for open position check.")
            return []

        all_positions = []

        # Go thought the given symbols and get position data for those
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
                            symbol = pos.get("symbol", "unknown")
                            side = pos.get("side") or None  # handle empty string here
                            avgPrice = pos.get("avgPrice", None)
                            leverage = float(pos.get("leverage", 1))
                            trailingStop = pos.get("trailingStop", None)
                            all_positions.append({
                                "symbol": symbol,
                                "side": side,
                                "size": size,
                                "avgPrice": avgPrice,
                                "leverage": leverage,
                                "trailingStop": trailingStop
                            })
            except Exception as inner_e:
                print(f"[ERROR] Failed to fetch position for {bybit_symbol}: {inner_e}")
                continue
        try:
            order_data = safe_load_json("logs/order_log.json")

            side_mapping = {
                "long": "Buy",
                "short": "Sell"
            }
            reverse_side_mapping = {v.lower(): k for k, v in side_mapping.items()}

            updated_any = False

            # Loop through positions, check that there is log order for every open position
            for position in all_positions:
                pos_symbol = position["symbol"]
                pos_side = position["side"]

                log_side_key = reverse_side_mapping.get(pos_side.lower(), "").lower()

                if pos_symbol not in order_data or log_side_key not in order_data[pos_symbol]:
                    order_data.setdefault(pos_symbol, {}).setdefault(log_side_key, [])

                existing_orders = order_data[pos_symbol][log_side_key]

                # Suodatetaan initiated-tilaiset orderit
                existing_orders, changed = filter_initiated_orders(existing_orders, pos_side)
                if changed:
                    updated_any = True

                has_initiated = any(o.get("status") == "initiated" for o in existing_orders)

                if not has_initiated:
                    print(f"No initiated orders for this symbol on the log")
                    complete_orders = [o for o in existing_orders if o.get("status") == "completed"]
                    if complete_orders:
                        latest_order = sorted(complete_orders, key=lambda x: x["timestamp"], reverse=True)[0]
                        latest_order["status"] = "initiated"
                        with open("logs/order_log.json", "w") as f:
                            json.dump(order_data, f, indent=4)
                        updated_any = True
                        print(f"🔄 Re-activated completed order as initiated for {pos_symbol} {log_side_key}")
                    else:
                        log_trade(
                            symbol=pos_symbol,
                            direction=log_side_key,
                            qty=position["size"],
                            price=0.0,
                            cost=0.0,
                            leverage=0,
                            platform=platform,
                            status="initiated"
                        )
                        updated_any = True
                        print(f"🆕 Created new initiated order for {pos_symbol} {log_side_key}")

            # Update orders to complete if no position found
            for sym_key, sides in order_data.items():
                for side_key, orders in sides.items():
                    for order in orders:
                        if order.get("status") != "completed":
                            expected_pos_side = side_mapping.get(side_key.lower())
                            match_found = any(
                                pos["symbol"] == sym_key and pos["side"] == expected_pos_side
                                for pos in all_positions
                            )
                            if not match_found:
                                updated = update_order_status(order.get("timestamp"), "completed")
                                if updated:
                                    updated_any = True
                                else:
                                    print(f"[WARN] Could not update status for {order.get('timestamp')}")

            if updated_any:
                print("✅ Updated order statuses\n.")
            else:
                print("ℹ️  No order statuses needed updating.\n")

        except Exception as e:
            print(f"[ERROR] Failed to update order status logs: {e}")
            traceback.print_exc()

        return all_positions

    except Exception as e:
        print(f"[ERROR] Failed to fetch positions: {e}")
        traceback.print_exc()
        return []

import os

def stop_loss_checker(positions):
    
    print(f"\n🔍 Doing stop loss checks and updates...")

    # Polku konfiguraatiotiedostoon
    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "stoploss_config.json")
    config_path = os.path.abspath(config_path)

    try:

        with open(config_path, "r") as cf:
            config = json.load(cf)

        # Get stop loss values from log
        set_sl_percent = parse_percent(config.get("set_stoploss_percent", "0.15%"))
        partial_sl_percent = parse_percent(config.get("partial_stoploss_percent", "0.15%"))
        trailing_percent = parse_percent(config.get("trailing_stoploss_percent", "0.15%"))

        if not positions:
            print("⚠️  No open positions passed to process_stop_loss_logic.")
            return

        with open("logs/order_log.json", "r") as f:
            order_data = json.load(f)

        # Loop through the positions
        for position in positions:

            # Get position info
            symbol = position['symbol']
            side = position['side']
            size = position['size']
            avg_price = float(position['avgPrice'])
            leverage = position['leverage']
            trailing_stop = position['trailingStop']

            # Get matching orders from log
            symbol_usdt = symbol.replace("USDC", "USDT")
            side_mapping = {"Buy": "long", "Sell": "short"}
            mapped_side = side_mapping.get(side)
            if not mapped_side:
                print(f"[WARNING] Unknown side '{side}' for {symbol}, skipping.")
                continue

            symbol_orders = order_data.get(symbol_usdt, {})
            orders = symbol_orders.get(mapped_side, [])

            if not orders:
                print(f"[INFO] No matching orders for {symbol_usdt} ({mapped_side})")
                continue

            # Go throught the orders
            for order in orders:

                # Skip completed
                if order.get("status") == "completed":
                    continue

                try:

                    # Run stop loss updater
                    process_stop_loss_logic(
                        symbol=symbol,
                        side=side,
                        size=size,
                        entry_price=avg_price,
                        leverage=leverage,
                        trailing_stop=trailing_stop,
                        set_sl_percent=set_sl_percent,
                        partial_sl_percent=partial_sl_percent,
                        trailing_percent=trailing_percent
                    )

                except Exception as e:
                    print(f"[ERROR] Failed to process order for {symbol}: {e}")

    except Exception as e:
        print(f"[ERROR] Could not check open order prices: {e}")
