import math
from integrations.binance_api_client import client, get_current_price
from configs import config

def round_step_size(quantity, step_size):
    precision = int(round(-math.log10(step_size), 0))
    return round(quantity, precision)

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
