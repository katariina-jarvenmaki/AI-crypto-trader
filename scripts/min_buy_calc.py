# scripts/min_buy_calc.py

import math
from integrations.binance_api_client import client
from integrations.bybit_api_client import get_bybit_price, get_bybit_symbol_info, round_bybit_quantity
from configs import config

def round_step_size(quantity, step_size):
    precision = int(round(-math.log10(step_size), 0))
    return round(quantity, precision)

def get_current_price(symbol):
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker["price"])
    except Exception as e:
        print(f"❌ Failed to fetch price for symbol {symbol}: {e}")
        return None

def calculate_minimum_valid_purchase(symbol):
    try:
        price = get_current_price(symbol)
        if not price:
            print(f"❌ Price not available for symbol {symbol}")
            return None

        exchange_info = client.get_symbol_info(symbol)
        if not exchange_info:
            print(f"❌ Symbol info not available for symbol {symbol}")
            return None

        filters = {f["filterType"]: f for f in exchange_info["filters"]}
        step_size = float(filters["LOT_SIZE"]["stepSize"])
        min_qty = float(filters["LOT_SIZE"]["minQty"])
        tick_size = float(filters["PRICE_FILTER"]["tickSize"])

        # ✅ Use MIN_NOTIONAL filter if available, otherwise fallback from config
        if "MIN_NOTIONAL" in filters and "minNotional" in filters["MIN_NOTIONAL"]:
            min_notional = float(filters["MIN_NOTIONAL"]["minNotional"])
        else:
            min_notional = config.DEFAULT_MIN_NOTIONAL
            # print(f"⚠️  MIN_NOTIONAL filter missing for symbol {symbol}, using default {min_notional}")

        qty = min_qty
        cost = qty * price

        while cost < min_notional:
            qty += step_size
            qty = round_step_size(qty, step_size)
            cost = qty * price

            if qty > 10_000:
                print("⚠️ Safety limit reached, something went wrong")
                return None

        return {
            "symbol": symbol,
            "qty": qty,
            "price": round(price, int(-math.log10(tick_size))),
            "cost": round(cost, 2),
            "step_size": step_size
        }

    except Exception as e:
        print(f"❌ Error calculating minimum purchase: {e}")
        return None

def calculate_minimum_valid_bybit_purchase(symbol):

    info = get_bybit_symbol_info(symbol)
    if info is None:
        print(f"❌ No Bybit symbol info found for symbol {symbol}")
        return None
    try:
        exchange_info = get_bybit_symbol_info(symbol)
        price = get_bybit_price(symbol)

        if not exchange_info or not price:
            return None

        lot_size_filter = exchange_info.get("lotSizeFilter", {})

        min_order_qty_raw = lot_size_filter.get("minOrderQty")
        qty_step_raw = lot_size_filter.get("qtyStep")

        if min_order_qty_raw is None or qty_step_raw is None:
            raise ValueError(f"❌ Missing or incomplete lotSizeFilter data for symbol {symbol}: {lot_size_filter}")

        # ✅ Convert before using
        min_qty = float(min_order_qty_raw)
        step_size = float(qty_step_raw)

        min_notional = 5.0  # assumed 5 USD, can be fetched more precisely

        qty = min_qty
        cost = qty * price

        # 🖨️ Print data for inspection
        while cost < min_notional:
            qty += step_size
            qty = round_step_size(qty, step_size)
            cost = qty * price

            if qty > 10000:
                print("⚠️ Safety limit reached in Bybit purchase")
                return None
                
        return {
            "qty": qty,
            "price": round(price),
            "cost": round(cost),
            "step_size": step_size
        }

    except Exception as e:
        print(f"❌ Error calculating minimum Bybit purchase: {e}")
        return None
