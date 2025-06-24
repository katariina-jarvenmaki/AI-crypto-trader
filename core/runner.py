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
from scripts.spot_order_handler import place_spot_trade_with_tp_sl
from scripts.min_buy_calc import calculate_minimum_valid_purchase, calculate_minimum_valid_bybit_purchase
from integrations.bybit_api_client import place_leveraged_bybit_order, get_available_balance, get_bybit_symbol_info, client as bybit_client
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
    print(f"📌 Signal: {final_signal}")
    print(f"📌 Mode: {final_signal}")
    print(f"📌 Interval: {interval}")
    print(f"📌 RSI: {rsi}")

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
        status = "complete"
    else:
        # Määrittele dynaaminen volyymikerroin
        if (market_state in ("unknown", "bear") and final_signal == "buy") or \
        (market_state in ("unknown", "bull") and final_signal == "sell"):
            volume_multiplier = 1.2
        elif (market_state == "neutral_sideways" and final_signal in ("buy", "sell")):
            volume_multiplier = 1.1
        else:
            volume_multiplier = 1.0
        risk_strength = check_riskmanagement(symbol=symbol, signal=final_signal, volume_multiplier=volume_multiplier)
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

    # Only log if signal is not from log or override
    if risk_strength in ("strong", "weak", "none") and mode not in ("log", "override"):
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
            status=status  # "complete" tai "rejected"
        )

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

    # Calculate the pricegit 
    if risk_strength == "strong" and final_signal == "buy":
        result = calculate_minimum_valid_purchase(symbol)
        quantity = "{:.8f}".format(result['qty'])

        # Laske osto ja tee kaupat
        if result:
            print(f"✅ Minimiosto laskettu {symbol}: {quantity} kpl @ {result['price']:.4f} → yhteensä {result['cost']:.2f} USD")
            
            # order_result = place_spot_trade_with_tp_sl(
            #     symbol=symbol,
            #     qty=quantity,
            #     entry_price=result["price"],
            #     tick_size=result["step_size"]
            # )

            # if order_result:
            #     print(f"✅ Kauppa suoritettu ja TP/SL asetettu: TP @ {order_result['tp_price']}, SL @ {order_result['sl_price']}")
            # else:
            #     print(f"❌ Kaupan suoritus epäonnistui symbolille {symbol}")

            # Määritellään kolikkokohtainen leverage
            leverage_map = {
                "BTCUSDT": 7,
                "ETHUSDT": 4,
                "SOLUSDT": 4,
                "XRPUSDT": 3
            }

            # Oletusarvo muille
            default_leverage = 2

            # 🔁 Tee lisäksi Bybit-osto oikealla minimimäärällä
            bybit_symbol = symbol.replace("USDC", "USDT")
            bybit_result = calculate_minimum_valid_bybit_purchase(bybit_symbol)
            if bybit_result is None:
                print(f"❌ Bybit minimioston laskenta epäonnistui symbolille {bybit_symbol}")
                return

            balance = get_available_balance("USDT")
            if balance < bybit_result["cost"]:
                print(f"❌ Ei tarpeeksi saldoa (saldo: {balance} < {bybit_result['cost']})")
                return

            if bybit_result:
                print(f"📦 Bybit minimiosto laskettu: {bybit_result['qty']} kpl @ {bybit_result['price']} USD → {bybit_result['cost']} USD")

                # Haetaan symbolille leverage, tai käytetään oletusta
                leverage = leverage_map.get(bybit_symbol, default_leverage)

                bybit_order_result = place_leveraged_bybit_order(
                    client=bybit_client,
                    symbol=bybit_symbol,
                    qty=bybit_result["qty"],
                    price=bybit_result["price"],
                    leverage=leverage
                )

                if bybit_order_result:
                    print(f"✅ Bybit-kauppa suoritettu: TP @ {bybit_order_result['tp_price']}, SL @ {bybit_order_result['sl_price']}")

                    # ⬇️ TÄSSÄ LISÄTÄÄN LOKITUS
                    from scripts.trade_order_logger import log_trade
                    log_trade(
                        symbol=bybit_symbol,
                        direction="long",  # tai "short" dynaamisesti
                        qty=bybit_result["qty"],
                        price=bybit_result["price"], 
                        leverage=leverage
                    )

                else:
                    print(f"❌ Bybit-kaupan suoritus epäonnistui symbolille {bybit_symbol}")
            else:
                print(f"❌ Bybit minimioston laskenta epäonnistui symbolille {bybit_symbol}")