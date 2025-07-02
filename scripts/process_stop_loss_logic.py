# scripts/process_stop_loss_logic.py
import os
import json
from integrations.bybit_api_client import client

# Lue JSON-konfiguraatio tiedostosta
config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "stoploss_config.json")
config_path = os.path.abspath(config_path)

with open(config_path, "r") as f:
    stop_loss_config = json.load(f)

def get_stop_loss_values(symbol):
    config = stop_loss_config.get(symbol, {})
    default = stop_loss_config["default"]

    def parsed(s):
        return float(s.strip('%')) / 100

    def to_percent_str(f):
        return f"{f * 100:.4f}%"  # esim. 0.00005 -> "0.0050%"

    set_sl = parsed(config.get("set_stoploss_percent", default["set_stoploss_percent"]))
    partial_sl = parsed(config.get("partial_stoploss_percent", default["partial_stoploss_percent"]))
    trailing_sl = parsed(config.get("trailing_stoploss_percent", default["trailing_stoploss_percent"]))

    return {
        "set_stoploss_percent": set_sl,
        "partial_stoploss_percent": partial_sl,
        "trailing_stoploss_percent": trailing_sl,
        "formatted": {
            "set": to_percent_str(set_sl),
            "partial": to_percent_str(partial_sl),
            "trailing": to_percent_str(trailing_sl)
        }
    }

def process_stop_loss_logic(symbol, side, size, entry_price, leverage, trailing_stop, set_sl_percent, partial_sl_percent, trailing_percent, formatted=None):

    print(f"⚙️  Processing stop loss for {symbol} ({side})")
    if formatted is not None:
        print(f"➡️  Size: {size}, Entry: {entry_price}, Leverage: {leverage}, Stop loss: {stop_loss}, Trailing: {trailing_stop}, "
              f"Set stop loss percent: {formatted['set']}, Partial stop loss percent: {formatted['partial']}, "
              f"Trailing stop loss percent: {formatted['trailing']}")
    else:
        print(f"➡️  Size: {size}, Entry: {entry_price}, Leverage: {leverage}, Stop loss: {stop_loss}, Trailing: {trailing_stop}, "
              f"Set stop loss percent: {set_sl_percent}, Partial stop loss percent: {partial_sl_percent}, "
              f"Trailing stop loss percent: {trailing_percent}")

    # Get live price
    price_data = client.get_tickers(category="linear", symbol=symbol)
    if "result" in price_data and "list" in price_data["result"]:
        last_price = float(price_data["result"]["list"][0]["lastPrice"])
    else:
        print(f"[WARN] No price data found for {symbol}")
        return []

    # Define direction
    if side == "Buy":
        target_price = entry_price * (1 + set_sl_percent)
        condition_met = last_price > target_price
        position_idx = 1
        direction = "long"
    elif side == "Sell":
        target_price = entry_price * (1 - set_sl_percent)
        condition_met = last_price < target_price
        position_idx = 2
        direction = "short"
    else:
        print(f"[WARN] Unknown direction for {symbol}: {side}")  # Käytetään side, ei direction
        return []

    print(f"🔸 {symbol} | Dir: {direction.upper()} | Entry: {entry_price:.4f} | Target: {target_price:.4f} | Live: {last_price:.4f}")

    if condition_met:
        print(f"✅ Trigger condition met for {symbol} ({direction})")

        # Defining the partial stop loss
        sl_offset = entry_price * partial_sl_percent
        if direction == "long":
            partial_sl_price = entry_price + sl_offset
        else:
            partial_sl_price = entry_price - sl_offset
        print(f"🔒 Setting partial SL to {partial_sl_price:.4f}")

        # Defining the trailing stop loss
        symbol_info = get_bybit_symbol_info(bybit_symbol)
        if symbol_info and "tickSize" in symbol_info:
            tick_size = float(symbol_info["tickSize"])
        else:
            print(f"[WARN] No symbol info or tickSize found for {bybit_symbol}, defaulting to 0.01")
            tick_size = 0.01
        trail_amount = last_price * trailing_percent
        trail_ticks = max(1, int(trail_amount / tick_size))
        print(f"📉 Setting trailing SL at {trailing_percent * 100:.2f}% → {trail_ticks} ticks")

        try:

            # Setting partial stop losses
            partial_body = {
                "category": "linear",
                "symbol": symbol,
                "stopLoss": str(round(partial_sl_price, 4)),
                "slSize": str(size),
                "slTriggerBy": "LastPrice",
                "tpslMode": "Partial",
                "positionIdx": position_idx
            }
            print(f"📤 Sending partial SL update: {partial_body}")
            response_partial = client.set_trading_stop(**partial_body)
            print(f"🟢 Partial SL updated: {response_partial}")

            # Full stop loss
            full_body = {
                "category": "linear",
                "symbol": symbol,
                "stopLoss": str(round(partial_sl_price, 4)),
                "slSize": str(size),
                "slTriggerBy": "LastPrice",
                "tpslMode": "Full",
                "positionIdx": position_idx
            }
            print(f"📤 Sending full SL update: {full_body}")
            response_full = client.set_trading_stop(**full_body)
            print(f"🟢 Full SL updated: {response_full}")

            trailing_body = {
                "category": "linear",
                "symbol": symbol,
                "trailingStop": str(trail_ticks),
                "tpslMode": "Full",
                "positionIdx": position_idx
            }

            print(f"📤 Sending trailing SL update: {trailing_body}")
            response_trailing = client.set_trading_stop(**trailing_body)
            print(f"🟢 Trailing SL updated: {response_trailing}")

        except Exception as sl_err:
            print(f"[ERROR] Failed to update stop loss: {sl_err}")

    else:
        print("⏳ Condition not yet met.")




    # 🔽 Lisää tähän varsinainen SL-logiikka — esimerkki:
    # - aseta uusi SL prosenttipohjaisesti
    # - päivitä trailing stop tarvittaessa
    # - vertaile markkinahintaan, jne.

    # new_stop_loss = None  # Esimerkkinä placeholder

    # TODO: Tähän varsinainen laskenta/päätöksenteko
    # Example logiikka:
    # stop_loss_price = entry_price * (1 - 0.02)  # 2% SL

    # return {
    #     "symbol": symbol,
    #    "side": side,
