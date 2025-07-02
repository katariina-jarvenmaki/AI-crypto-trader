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
        print(f"[WARN] Unknown direction for {symbol}: {side}")
        return []

    threshold_amount = entry_price * threshold_percent

    # Skip logic: decide whether full SL or trailing SL need updates
    skip_full_sl = False
    skip_trailing = False

    if direction == "long":
        if stop_loss >= full_sl_price or (full_sl_price - stop_loss) < threshold_amount:
            skip_full_sl = True
        if trailing_stop > 0:
            skip_trailing = True
    else:
        if stop_loss <= full_sl_price or (stop_loss - full_sl_price) < threshold_amount:
            skip_full_sl = True
        if trailing_stop > 0:
            skip_trailing = True

    # If both updates can be skipped, exit early
    if skip_full_sl and skip_trailing:
        print("⏩ Skipping both full SL and trailing SL updates – no significant change needed.")
        return []

    # Get current price
    price_data = client.get_tickers(category="linear", symbol=symbol)
    if "result" in price_data and "list" in price_data["result"]:
        last_price = float(price_data["result"]["list"][0]["lastPrice"])
    else:
        print(f"[WARN] No price data found for {symbol}")
        return []

    if direction == "long":
        condition_met = last_price > target_price
    else:
        condition_met = last_price < target_price

    print(f"🔸 {symbol} | Dir: {direction.upper()} | Entry: {entry_price:.4f} | Target: {target_price:.4f} | Live: {last_price:.4f}")

    if condition_met:
        print(f"✅ Trigger condition met for {symbol} ({direction})")

        try:
            if not skip_full_sl:
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
            else:
                print("⏩ Skipping full SL update.")

            if not skip_trailing:
                trail_amount = entry_price * trailing_percent
                trailingStop = to_str(trail_amount)
                trailing_body = {
                    "category": "linear",
                    "symbol": symbol,
                    "trailingStop": trailingStop,
                    "tpslMode": "Full",
                    "positionIdx": position_idx
                }
                print(f"📤 Sending trailing SL update: {trailing_body}")
                response_trailing = client.set_trading_stop(**trailing_body)
                print(f"🟢 Trailing SL updated: {response_trailing}")
            else:
                print("⏩ Skipping trailing SL update.")

        except Exception as sl_err:
            print(f"[ERROR] Failed to update stop loss: {sl_err}")

    else:
        print("⏳ Condition not yet met.")

