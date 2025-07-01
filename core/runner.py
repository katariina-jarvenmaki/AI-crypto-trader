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
from scripts.trade_order_logger import load_trade_logs, update_order_status, safe_load_json
from scripts.sorting import sort_orders_by_stoploss_priority

def normalize_symbol(symbol):
    # Voit säätää tätä logiikkaa lisää tarpeen mukaan
    return symbol.replace("USDC", "USDT")

def check_and_reactivate_orders(bybit_client, symbols_to_check=None, platform=None, order_data_path="logs/order_log.json"):
    import json

    with open(order_data_path, "r") as f:
        order_data = json.load(f)

    positions_response = bybit_client.get_positions(
        category="linear",
        settleCoin="USDT"
    )

    positions = positions_response.get("result", {}).get("list", [])
    bybit_open_symbols = {
        normalize_symbol(pos.get("symbol")) for pos in positions
        if float(pos.get("size", 0)) > 0
    }

    print(f"[DEBUG] Aktiiviset Bybit-positiot: {bybit_open_symbols}")

    if symbols_to_check is not None:
        symbols_to_check = {normalize_symbol(s) for s in symbols_to_check}
        bybit_open_symbols = bybit_open_symbols.intersection(symbols_to_check)

    updated = False
    for symbol in bybit_open_symbols:
        if symbol in order_data:
            for direction in ["long", "short"]:
                orders = order_data[symbol][direction]
                has_active = any(o.get("status") != "complete" for o in orders)
                if has_active:
                    continue
                complete_orders = [o for o in orders if o.get("status") == "complete"]
                if complete_orders:
                    latest_order = max(complete_orders, key=lambda x: x.get("timestamp", ""))
                    latest_order["status"] = "initiated"
                    updated = True
                    print(f"[INFO] Uudelleenaktivoitu {symbol} {direction.upper()} → INITIATED")
        else:
            print(f"[DEBUG] Symbolia {symbol} ei löytynyt order_log.jsonista")

    if updated:
        with open(order_data_path, "w") as f:
            json.dump(order_data, f, indent=4)

    return [
        {
            "symbol": pos.get("symbol"),
            "side": pos.get("side"),
            "size": pos.get("size")
        }
        for pos in positions
        if normalize_symbol(pos.get("symbol")) in bybit_open_symbols and float(pos.get("size", 0)) > 0
    ]

def stop_loss_updater():
    import os
    import json
    from integrations.bybit_api_client import parse_percent, get_bybit_symbol_info
    from core.runner import bybit_client

    def get_symbol_config(config, symbol, key, default_key="default"):
        return config.get(symbol, {}).get(key, config.get(default_key, {}).get(key))

    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "stoploss_config.json")
    config_path = os.path.abspath(config_path)

    try:
        with open("logs/order_log.json", "r") as f:
            order_data = json.load(f)

        # Palauta viimeisin "complete" status takaisin "initated" jos positio taas näkyy Bybitissä
        positions_response = bybit_client.get_positions(
            category="linear",
            settleCoin="USDT"
        )

        positions = positions_response.get("result", {}).get("list", [])
        bybit_open_symbols = {
            pos.get("symbol") for pos in positions
            if float(pos.get("size", 0)) > 0
        }

        updated = False
        for symbol in bybit_open_symbols:
            if symbol in order_data:
                for direction in ["long", "short"]:
                    orders = order_data[symbol][direction]
                    complete_orders = [o for o in orders if o.get("status") == "complete"]
                    if complete_orders:
                        latest_order = max(complete_orders, key=lambda x: x.get("timestamp", ""))
                        latest_order["status"] = "initated"
                        updated = True
                        print(f"[INFO] Re-activated {symbol} {direction.upper()} order from complete → INITIATED")

        if updated:
            with open("logs/order_log.json", "w") as f:
                json.dump(order_data, f, indent=4)

        # Lataa konfiguraatio stoploss-logiikkaa varten
        with open(config_path, "r") as cf:
            config = json.load(cf)

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

                        # Hae reaaliaikainen hinta
                        price_data = bybit_client.get_tickers(category="linear", symbol=bybit_symbol)
                        if "result" in price_data and "list" in price_data["result"]:
                            last_price = float(price_data["result"]["list"][0]["lastPrice"])
                        else:
                            print(f"[WARN] No price data found for {bybit_symbol}")
                            continue

                        # Ticksize symbolitiedoista
                        symbol_info = get_bybit_symbol_info(bybit_symbol)
                        tick_size = float(symbol_info.get("tickSize", 0.01)) if symbol_info else 0.01
                        if not symbol_info:
                            print(f"[WARN] No symbol info or tickSize found for {bybit_symbol}, defaulting to 0.01")

                        set_sl_percent = parse_percent(get_symbol_config(config, bybit_symbol, "set_stoploss_percent"))

                        if direction == "long":
                            position_idx = 1
                            target_price = entry_price * (1 + set_sl_percent)
                            condition_met = last_price > target_price
                        elif direction == "short":
                            position_idx = 2
                            target_price = entry_price * (1 - set_sl_percent)
                            condition_met = last_price < target_price
                        else:
                            print(f"[WARN] Unknown direction for {bybit_symbol}: {direction}")
                            continue

                        print(f"🔸 {symbol_key} | Dir: {direction.upper()} | Entry: {entry_price:.4f} | Target: {target_price:.4f} | Live: {last_price:.4f}")

                        if condition_met:
                            print(f"✅ Trigger condition met for {symbol_key} ({direction})")

                            # SL-hinta
                            partial_sl_percent = parse_percent(get_symbol_config(config, bybit_symbol, "partial_stoploss_percent"))
                            partial_sl_price = entry_price * (1 + partial_sl_percent) if direction == "long" else entry_price * (1 - partial_sl_percent)
                            print(f"🔒 Setting partial SL to {partial_sl_price:.4f}")

                            # Hae koko position koko
                            position_info = bybit_client.get_position_info(symbol=bybit_symbol)
                            position_size = int(float(position_info["size"]))

                            # Trailing laskenta
                            trailing_percent = parse_percent(get_symbol_config(config, bybit_symbol, "trailing_stoploss_percent"))
                            trail_amount = last_price * trailing_percent
                            trail_ticks = max(1, int(trail_amount / tick_size))

                            # Bybit min trailing: ≥ 10 % hinnasta
                            min_trailing = last_price * 0.10
                            if trail_amount < min_trailing:
                                print(f"[WARN] Trailing stop {trail_amount:.4f} too small (<10% of {last_price:.4f}), skipping trailing SL")
                                trail_ticks = None

                            # Partial SL
                            partial_body = {
                                "category": "linear",
                                "symbol": bybit_symbol,
                                "stopLoss": str(round(partial_sl_price, 4)),
                                "slSize": str(position_size),
                                "slTriggerBy": "LastPrice",
                                "tpslMode": "Partial",
                                "positionIdx": position_idx
                            }

                            print(f"📤 Sending partial SL update: {partial_body}")
                            response_partial = bybit_client.set_trading_stop(**partial_body)
                            print(f"🟢 Partial SL updated: {response_partial}")

                            # Trailing SL (jos validi)
                            if trail_ticks:
                                trailing_body = {
                                    "category": "linear",
                                    "symbol": bybit_symbol,
                                    "trailingStop": str(trail_ticks),
                                    "tpslMode": "Full",
                                    "positionIdx": position_idx
                                }

                                print(f"📤 Sending trailing SL update: {trailing_body}")
                                response_trailing = bybit_client.set_trading_stop(**trailing_body)
                                print(f"🟢 Trailing SL updated: {response_trailing}")

                        else:
                            print("⏳ Condition not yet met.")

                    except Exception as price_err:
                        print(f"[ERROR] Failed to get price for {bybit_symbol}: {price_err}")

    except Exception as e:
        print(f"[ERROR] Could not check open order prices: {e}")