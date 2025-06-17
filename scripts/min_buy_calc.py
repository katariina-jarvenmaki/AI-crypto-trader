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
        print(f"❌ Hintahaku epäonnistui symbolille {symbol}: {e}")
        return None

def calculate_minimum_valid_purchase(symbol):
    try:
        price = get_current_price(symbol)
        if not price:
            print(f"❌ Hinta ei saatavilla symbolille {symbol}")
            return None

        exchange_info = client.get_symbol_info(symbol)
        if not exchange_info:
            print(f"❌ Symbolitietoja ei saatavilla symbolille {symbol}")
            return None

        filters = {f["filterType"]: f for f in exchange_info["filters"]}
        step_size = float(filters["LOT_SIZE"]["stepSize"])
        min_qty = float(filters["LOT_SIZE"]["minQty"])
        tick_size = float(filters["PRICE_FILTER"]["tickSize"])

        # ✅ Käytetään MIN_NOTIONAL-filtteriä jos saatavilla, muuten fallback configista
        if "MIN_NOTIONAL" in filters and "minNotional" in filters["MIN_NOTIONAL"]:
            min_notional = float(filters["MIN_NOTIONAL"]["minNotional"])
        else:
            min_notional = config.DEFAULT_MIN_NOTIONAL
            print(f"⚠️  MIN_NOTIONAL-filter puuttuu symbolilta {symbol}, käytetään oletusarvoa {min_notional}")

        qty = min_qty
        cost = qty * price

        while cost < min_notional:
            qty += step_size
            qty = round_step_size(qty, step_size)
            cost = qty * price

            if qty > 10_000:
                print("⚠️ Turvaraja saavutettu, jokin meni pieleen")
                return None

        return {
            "symbol": symbol,
            "qty": qty,
            "price": round(price, int(-math.log10(tick_size))),
            "cost": round(cost, 2),
            "step_size": step_size
        }

    except Exception as e:
        print(f"❌ Virhe minimioston laskennassa: {e}")
        return None


def calculate_minimum_valid_bybit_purchase(symbol):
    info = get_bybit_symbol_info(symbol)
    if info is None:
        print(f"❌ Bybit-symbolitietoa ei löytynyt symbolille {symbol}")
        return None
    try:
        exchange_info = get_bybit_symbol_info(symbol)
        price = get_bybit_price(symbol)

        if not exchange_info or not price:
            return None

        lot_size_filter = exchange_info.get("lot_size_filter", {})
        min_qty = float(lot_size_filter.get("min_order_qty", 0.001))
        step_size = float(lot_size_filter.get("qty_step", 0.001))

        min_notional = 5.0  # oletetaan 5 USD, voidaan hakea tarkemmin

        qty = min_qty
        cost = qty * price

        while cost < min_notional:
            qty += step_size
            qty = round_step_size(qty, step_size)
            cost = qty * price

            if qty > 10000:
                print("⚠️ Turvaraja Bybitin ostossa saavutettu")
                return None

        return {
            "qty": qty,
            "price": round(price, 2),
            "cost": round(cost, 2),
            "step_size": step_size
        }

    except Exception as e:
        print(f"❌ Bybitin minimioston laskentavirhe: {e}")
        return None
