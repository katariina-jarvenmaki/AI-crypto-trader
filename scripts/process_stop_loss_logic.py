# scripts/process_stop_loss_logic.py
import os
import json
from integrations.bybit_api_client import client, get_bybit_symbol_info

# Lue JSON-konfiguraatio tiedostosta
config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "stoploss_config.json")
config_path = os.path.abspath(config_path)

with open(config_path, "r") as f:
    stop_loss_config = json.load(f)

def parsed(s):
    return float(s.strip('%')) / 100

def to_percent_str(f):
    return f"{f * 100:.4f}%"  # esim. 0.00005 -> "0.0050%"

def to_str(f):
    return f"{f * 100:.4f}" 

def get_stop_loss_values(symbol):
    config = stop_loss_config.get(symbol, {})
    default = stop_loss_config["default"]

    set_sl = parsed(config.get("set_stoploss_percent", default["set_stoploss_percent"]))
    full_sl = parsed(config.get("full_stoploss_percent", default["full_stoploss_percent"]))
    trailing_sl = parsed(config.get("trailing_stoploss_percent", default["trailing_stoploss_percent"]))
    threshold = parsed(config.get("min_stop_loss_diff_percent", default.get("min_stop_loss_diff_percent", "0.001%")))

    return {
        "set_stoploss_percent": set_sl,
        "full_stoploss_percent": full_sl,
        "trailing_stoploss_percent": trailing_sl,
        "min_stop_loss_diff_percent": threshold,  # ← tämä lisättiin
        "formatted": {
            "set": to_percent_str(set_sl),
            "full": to_percent_str(full_sl),
            "trailing": to_percent_str(trailing_sl),
            "min_diff": to_percent_str(threshold)
        }
    }

def process_stop_loss_logic(symbol, side, size, entry_price, leverage, stop_loss, trailing_stop, set_sl_percent, full_sl_percent, trailing_percent, threshold_percent, formatted=None):

    print(f"⚙️  Processing stop loss for {symbol} ({side})")
    if formatted is not None:
        print(f"➡️  Size: {size}, Entry: {entry_price}, Leverage: {leverage}, Stop loss: {stop_loss}, Trailing: {trailing_stop}, "
            f"Set stop loss percent: {formatted['set']}, Stop loss percent: {formatted['full']}, "
            f"Trailing stop loss percent: {formatted['trailing']}, Threshold percent: {formatted['min_diff']}")
    else:
        print(f"➡️  Size: {size}, Entry: {entry_price}, Leverage: {leverage}, Stop loss: {stop_loss}, Trailing: {trailing_stop}, "
            f"Set stop loss percent: {formatted['set']}, Stop loss percent: {formatted['full']}, "
            f"Trailing stop loss percent: {formatted['trailing']}, Threshold percent: {formatted['min_diff']}")

    # Define direction and full stop loss
    sl_offset = entry_price * full_sl_percent
    if side == "Buy":
        direction = "long"
        target_price = entry_price * (1 + set_sl_percent)
        full_sl_price = entry_price + sl_offset
        position_idx = 1
    elif side == "Sell":
        direction = "short"
        target_price = entry_price * (1 - set_sl_percent)
        full_sl_price = entry_price - sl_offset
        position_idx = 2
    else:
        print(f"[WARN] Unknown direction for {symbol}: {side}")  # Käytetään side, ei direction
        return []

    # Skip stop loss update if current one is better or change is too small
    threshold_amount = entry_price * threshold_percent
    if direction == "long":
        if stop_loss >= full_sl_price and trailing_stop > 0:
            print(f"⏩ Skipping update: current stop loss ({stop_loss}) is better than or equal to new ({full_sl_price})")
            return []
        if (full_sl_price - stop_loss) < threshold_amount:
            print(f"⏩ Skipping update: change ({full_sl_price - stop_loss:.8f}) is smaller than threshold ({threshold_amount:.8f})")
            return []
    elif direction == "short":
        if stop_loss <= full_sl_price and trailing_stop > 0:
            print(f"⏩ Skipping update: current stop loss ({stop_loss}) is better than or equal to new ({full_sl_price})")
            return []
        if (stop_loss - full_sl_price) < threshold_amount:
            print(f"⏩ Skipping update: change ({stop_loss - full_sl_price:.8f}) is smaller than threshold ({threshold_amount:.8f})")
            return []

    # Get live price
    price_data = client.get_tickers(category="linear", symbol=symbol)
    if "result" in price_data and "list" in price_data["result"]:
        last_price = float(price_data["result"]["list"][0]["lastPrice"])
    else:
        print(f"[WARN] No price data found for {symbol}")
        return []

    # Define direction
    if direction == "long":
        condition_met = last_price > target_price
    elif direction == "short":
        condition_met = last_price < target_price

    print(f"🔸 {symbol} | Dir: {direction.upper()} | Entry: {entry_price:.4f} | Target: {target_price:.4f} | Live: {last_price:.4f}")

    if condition_met:
        print(f"✅ Trigger condition met for {symbol} ({direction})")

        # Defining the full stop loss
        if direction == "long":
            full_sl_price = entry_price + sl_offset
        else:
            full_sl_price = entry_price - sl_offset
        print(f"🔒 Setting full SL to {full_sl_price:.4f}")

        # Defining the trailing stop loss
        trail_amount = entry_price * trailing_percent
        print(f"Trailing SL amount at {str(trail_amount)}")

        try:

            # Setting full stop loss
            full_body = {
                "category": "linear",
                "symbol": symbol,
                "stopLoss": str(round(full_sl_price, 4)),
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
                "trailingStop": str(trail_amount),
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
