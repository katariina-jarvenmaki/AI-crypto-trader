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
from scripts.process_stop_loss_logic import process_stop_loss_logic, get_stop_loss_values
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
from configs.binance_config import SUPPORTED_SYMBOLS
from scripts.unsupported_symbol_handler import handle_unsupported_symbol, get_latest_log_entry_for_symbol

# Symbol processing loop
def run_analysis_for_symbol(selected_symbols, symbol, is_first_run, initiated_counts, override_signal=None, volume_mode=None, long_only=False, short_only=False):

    # ⛔ Estä USDC-symbolit heti alkuun (jos niitä ei ole tarkoitus käsitellä suoraan)
    if symbol.endswith("USDC"):
        return

    print(f"\n🔍 Processing symbol: {symbol}")
    symbol = symbol.replace("USDT", "USDC")

    # ✅ Check if symbol is unsupported and handle it
    if symbol not in SUPPORTED_SYMBOLS:
        handle_unsupported_symbol(symbol, long_only, short_only, selected_symbols)
        return

    # Get the signals for the symbols
    signal_info = get_signal(
        symbol=symbol,
        interval=None,
        rsi=None,
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
    bybit_symbol = symbol.replace("USDC", "USDT")
    ohlcv_entry = get_latest_log_entry_for_symbol("integrations/multi_interval_ohlcv/ohlcv_fetch_log.jsonl", bybit_symbol)
    price_entry = get_latest_log_entry_for_symbol("integrations/price_data_fetcher/price_data_log.jsonl", bybit_symbol)
    history_analysis_entry = get_latest_log_entry_for_symbol("modules/history_analyzer/history_analysis_log.jsonl", bybit_symbol)
    if risk_strength in ("strong", "weak", "none") and (
        mode not in ("momentum", "log", "override") or ((mode == "log" or mode == "momentum") and status == "completed")
    ):
        now = datetime.now(pytz.timezone(TIMEZONE.zone))
        update_signal_log(
            symbol=symbol,
            interval=interval,
            rsi=rsi,
            signal_type=final_signal,
            mode=mode,
            now=now,
            status=status,
            momentum_strength=risk_strength,
            reverse_signal_info=reverse_result,
            volume_multiplier=volume_multiplier,
            price_change=selected_change_text,
            market_state=market_state,
            started_on=started_on,
            ohlcv_data=ohlcv_entry,
            price_data=price_entry,
            history_analysis_data=history_analysis_entry
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
                rsi=rsi,
                mode=mode,
                market_state=market_state,
                started_on=started_on,
                momentum_strength=risk_strength,
                price_change=selected_change_text,
                volume_multiplier=volume_multiplier,
                reverse_signal_info=reverse_result,
                ohlcv_data=ohlcv_entry,
                price_data=price_entry,
                history_analysis_data=history_analysis_entry
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
                rsi=rsi,
                mode=mode,
                market_state=market_state,
                started_on=started_on,
                momentum_strength=risk_strength,
                price_change=selected_change_text,
                volume_multiplier=volume_multiplier,
                reverse_signal_info=reverse_result,
                ohlcv_data=ohlcv_entry,
                price_data=price_entry,
                history_analysis_data=history_analysis_entry
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
                rsi=rsi,
                mode=mode,
                market_state=market_state,
                started_on=started_on,
                momentum_strength=risk_strength,
                price_change=selected_change_text,
                volume_multiplier=volume_multiplier,
                reverse_signal_info=reverse_result,
                ohlcv_data=ohlcv_entry,
                price_data=price_entry,
                history_analysis_data=history_analysis_entry
            )

import json
import traceback
import pandas as pd
from scripts.trade_order_logger import (
    load_trade_logs,
    update_order_status,
    safe_load_json,
    log_trade,
)

def fetch_all_positions_bybit():
    """Hakee kaikki lineaariset USDT-positiot Bybitistä käyttäen sivutusta."""
    all_positions = []
    cursor = None

    while True:
        params = {
            "category": "linear",
            "settleCoin": "USDT",
            "limit": 50  # Bybitin maksimi yhdelle sivulle
        }
        if cursor:
            params["cursor"] = cursor

        try:
            response = bybit_client.get_positions(**params)
            result = response.get("result", {})
            positions = result.get("list", [])
            all_positions.extend(positions)

            print(f"➡️  Retrieved {len(positions)} positions (Total so far: {len(all_positions)})")

            cursor = result.get("nextPageCursor")
            if not cursor:
                break

        except Exception as e:
            print(f"[ERROR] Failed to fetch positions: {e}")
            break

    return all_positions

def check_positions_and_update_logs(symbols_to_check=None, platform="ByBit"):
    try:
        if platform != "ByBit":
            print(f"[ERROR] Unsupported platform: {platform}")
            return []

        all_raw_positions = fetch_all_positions_bybit()

        all_positions = []

        for pos in all_raw_positions:
            try:
                size = float(pos.get("size", 0))
                status = pos.get("positionStatus", "").lower()
                symbol = pos.get("symbol", "unknown")
                side = pos.get("side", "").lower()

                if size > 0 and status == "normal":
                    avgPrice = float(pos.get("avgPrice", 0))
                    leverage = float(pos.get("leverage", 1))
                    stopLoss = pos.get("stopLoss")
                    trailingStop = pos.get("trailingStop")

                    all_positions.append({
                        "symbol": symbol,
                        "side": side,
                        "size": size,
                        "avgPrice": avgPrice,
                        "leverage": leverage,
                        "stopLoss": stopLoss,
                        "trailingStop": trailingStop
                    })

            except Exception as pos_e:
                print(f"[ERROR] Failed to process position: {pos_e}")

        try:
            order_data = safe_load_json("logs/order_log.json")

            side_mapping = {
                "long": "Buy",
                "short": "Sell"
            }
            reverse_side_mapping = {v.lower(): k for k, v in side_mapping.items()}

            updated_any = False

            for position in all_positions:
                pos_symbol = position["symbol"]
                pos_side = position["side"]

                log_side_key = reverse_side_mapping.get(pos_side.lower(), "").lower()
                if not log_side_key:
                    continue

                order_data.setdefault(pos_symbol, {}).setdefault(log_side_key, [])
                existing_orders = order_data[pos_symbol][log_side_key]

                existing_orders, changed = filter_initiated_orders(existing_orders, pos_side)
                if changed:
                    updated_any = True

                has_initiated = any(o.get("status") == "initiated" for o in existing_orders)

                if not has_initiated:
                    complete_orders = [o for o in existing_orders if o.get("status") == "completed"]
                    if complete_orders:
                        latest_order = sorted(complete_orders, key=lambda x: x.get("timestamp", 0), reverse=True)[0]
                        latest_order["status"] = "initiated"
                        with open("logs/order_log.json", "w") as f:
                            json.dump(order_data, f, indent=4)
                        updated_any = True
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

            for sym_key, sides in order_data.items():
                for side_key, orders in sides.items():
                    for order in orders:
                        if not isinstance(order, dict) or order.get("status") == "completed":
                            continue
                        expected_pos_side = side_mapping.get(side_key.lower())
                        match_found = any(
                            pos["symbol"] == sym_key and pos["side"] == expected_pos_side.lower()
                            for pos in all_positions
                        )
                        if not match_found:
                            updated = update_order_status(order.get("timestamp"), "completed")
                            if updated:
                                updated_any = True

            if updated_any:
                print("✅ Order log updated.")
            else:
                print("ℹ️  No changes to order log.")

        except Exception as log_e:
            print(f"[ERROR] Failed while updating logs: {log_e}")
            traceback.print_exc()

        print(f"📊 Total open positions found: {len(all_positions)}")
        return all_positions

    except Exception as e:
        print(f"[FATAL ERROR] Position check failed: {e}")
        traceback.print_exc()
        return []

import os
import json

def stop_loss_checker(positions):
    print(f"\n🔍 Doing stop loss checks and updates...")

    if not positions:
        print("⚠️  No open positions passed to process_stop_loss_logic.")
        return

    def safe_float(value, default=0.0):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    try:
        with open("logs/order_log.json", "r") as f:
            order_data = json.load(f)

        for position in positions:
            symbol = position.get('symbol')
            side = position.get('side')
            size = position.get('size')
            avg_price = safe_float(position.get('avgPrice'))
            leverage = position.get('leverage')
            stop_loss = safe_float(position.get('stopLoss', ''))
            trailing_stop = safe_float(position.get('trailingStop', ''))

            if not all([symbol, side, size, avg_price, leverage is not None]):
                print(f"[WARNING] Missing essential position data for {position}, skipping.")
                continue

            symbol_usdt = symbol.replace("USDC", "USDT")
            side_mapping = {"buy": "long", "sell": "short"}
            side_lower = side.lower()
            mapped_side = side_mapping.get(side_lower)

            if not mapped_side:
                print(f"[WARNING] Unknown side '{side}' for {symbol}, skipping.")
                continue

            symbol_orders = order_data.get(symbol_usdt, {})
            orders = symbol_orders.get(mapped_side, [])

            if not orders:
                print(f"[INFO] No matching orders for {symbol_usdt} ({mapped_side})")
                continue

            for order in orders:
                if order.get("status") == "completed":
                    continue

                try:
                    sl_values = get_stop_loss_values(symbol, mapped_side)

                    process_stop_loss_logic(
                        symbol=symbol,
                        side=mapped_side,  # ✅ Käytetään nyt oikein
                        size=size,
                        entry_price=avg_price,
                        leverage=leverage,
                        stop_loss=stop_loss,
                        trailing_stop=trailing_stop,
                        set_sl_percent=sl_values['set_stoploss_percent'],
                        full_sl_percent=sl_values['full_stoploss_percent'],
                        trailing_percent=sl_values['trailing_stoploss_percent'],
                        threshold_percent=sl_values['min_stop_loss_diff_percent'],
                        formatted=sl_values.get("formatted")
                    )

                except Exception as e:
                    print(f"[ERROR] Failed to process order for {symbol}: {e}")

    except Exception as e:
        print(f"[ERROR] Could not check open order prices: {e}")
