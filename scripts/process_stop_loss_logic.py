# scripts/process_stop_loss_logic.py
import os
import json
from integrations.bybit_api_client import client, get_bybit_symbol_info, get_bybit_symbol_price

# Lue JSON-konfiguraatio tiedostosta
config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "stoploss_config.json")
config_path = os.path.abspath(config_path)

def decimal_places(value):
    s = str(value)
    if '.' in s:
        return len(s.split('.')[1])
    return 0

with open(config_path, "r") as f:
    stop_loss_config = json.load(f)

def parsed(s):
    return float(s.strip('%')) / 100

def to_percent_str(f):
    return f"{f * 100:.4f}%"  # esim. 0.00005 -> "0.0050%"

def to_str(f):
    return f"{f * 100:.4f}" 

def get_stop_loss_values(symbol, side):
    config = stop_loss_config.get(symbol, {})
    default = stop_loss_config["default"]

    direction = side  # "long" tai "short"
    symbol_config = config.get(direction, {})
    default_config = default.get(direction, {})

    def get_val(key):
        return parsed(symbol_config.get(key, default_config.get(key, "0.001%")))

    set_sl = get_val("set_stoploss_percent")
    full_sl = get_val("full_stoploss_percent")
    trailing_sl = get_val("trailing_stoploss_percent")
    threshold = get_val("min_stop_loss_diff_percent")

    return {
        "set_stoploss_percent": set_sl,
        "full_stoploss_percent": full_sl,
        "trailing_stoploss_percent": trailing_sl,
        "min_stop_loss_diff_percent": threshold,
        "tight_sl_percent_long": get_val("tight_sl_percent_long"), 
        "tight_sl_percent_short": get_val("tight_sl_percent_short"),
        "formatted": {
            "set": to_percent_str(set_sl),
            "full": to_percent_str(full_sl),
            "trailing": to_percent_str(trailing_sl),
            "min_diff": to_percent_str(threshold)
        }
    }

def process_stop_loss_logic(symbol, side, size, entry_price, leverage, stop_loss, trailing_stop,
                            set_sl_percent, full_sl_percent, trailing_percent, threshold_percent,
                            tight_sl_percent_long, tight_sl_percent_short, formatted=None):

    sentiment_log_path = "../AI-crypto-trader-logs/analysis_logs/history_sentiment_log.jsonl"

    print(f"⚙️  Processing stop loss for {symbol} ({side})")
    if formatted is not None:
        print(f"➡️  Size: {size}, Entry: {entry_price}, Leverage: {leverage}, Stop loss: {stop_loss}, Trailing: {trailing_stop}, "
              f"Set stop loss percent: {formatted['set']}, Stop loss percent: {formatted['full']}, "
              f"Trailing stop loss percent: {formatted['trailing']}, Threshold percent: {formatted['min_diff']}")

    sl_offset = entry_price * full_sl_percent
    decimals = decimal_places(entry_price)
    trail_amount = entry_price * trailing_percent
    threshold_amount = entry_price * threshold_percent

    if side == "long":
        direction = "long"
        target_price = entry_price * (1 + set_sl_percent)
        full_sl_price = entry_price + sl_offset
        position_idx = 1
    elif side == "short":
        direction = "short"
        target_price = entry_price * (1 - set_sl_percent)
        full_sl_price = entry_price - sl_offset
        position_idx = 2
    else:
        print(f"[WARN] Unknown direction for {symbol}: {side}")
        return []

    skip_full_sl = False
    skip_trailing = False

    # Determine whether to skip full stop loss update
    if direction == "long":
        if stop_loss > 0 and (stop_loss >= full_sl_price or (full_sl_price - stop_loss) < threshold_amount):
            skip_full_sl = True
    else:
        if stop_loss > 0 and (stop_loss <= full_sl_price or (stop_loss - full_sl_price) < threshold_amount):
            skip_full_sl = True

    # Determine whether to skip trailing stop update
    if trailing_stop > 0:
        skip_trailing = True

    # Skip both only if neither update is necessary
    if skip_full_sl and skip_trailing:
        print("⏩ Skipping both full SL and trailing SL updates – no significant change needed.")
        return []

    # Get latest price
    price_data = client.get_tickers(category="linear", symbol=symbol)
    if "result" in price_data and "list" in price_data["result"]:
        last_price = float(price_data["result"]["list"][0]["lastPrice"])
    else:
        print(f"[WARN] No price data found for {symbol}")
        return []

    condition_met = (last_price > target_price) if direction == "long" else (last_price < target_price)

    print(f"🔸 {symbol} | Dir: {direction.upper()} | Entry: {entry_price:.{decimals}f} | "
          f"Target: {target_price:.{decimals}f} | Live: {last_price:.{decimals}f}  | Full SL: {full_sl_price:.{decimals}f}")

    if condition_met:
        print(f"✅ Trigger condition met for {symbol} ({direction})")

        # Try setting full stop loss
        if not skip_full_sl:
            try:
                full_sl_str = f"{full_sl_price:.{decimals}f}"
                full_body = {
                    "category": "linear",
                    "symbol": symbol,
                    "stopLoss": full_sl_str,
                    "slSize": str(size),
                    "slTriggerBy": "LastPrice",
                    "tpslMode": "Full",
                    "positionIdx": position_idx
                }
                print(f"📤 Sending full SL update: {full_body}")
                response_full = client.set_trading_stop(**full_body)
                print(f"🟢 Full SL updated: {response_full}")
            except Exception as e:
                print(f"[ERROR] Failed to update full SL: {e}")
        else:
            print("⏩ Skipping full SL update.")

        # Try setting trailing stop
        if not skip_trailing:
            trail_amount = entry_price * trailing_percent
            trailingStop = to_str(trail_amount)
            print(f"Calculated trailingStop: {trailingStop}")
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

    else:
        print("⏳ Condition not yet met.")

        config = stop_loss_config["default"][direction]
        excessive_sl_percent = parsed(config.get("excessive_stop_loss_percent", "30%")) / leverage

        excessive_sl = False
        missing_sl = stop_loss <= 0

        if direction == "long":
            excessive_sl = stop_loss > 0 and stop_loss < (entry_price - entry_price * 2 * full_sl_percent)
        elif direction == "short":
            excessive_sl = stop_loss > 0 and stop_loss > (entry_price + entry_price * 2 * full_sl_percent)

        if excessive_sl or missing_sl:
            print(f"⚠️  {'Missing' if missing_sl else 'Excessive'} SL detected.")

        # ⚠️ UUSI LOGIIKKA: Tiukka sentimenttipohjainen SL
        tight_sl_override = False
        new_sl_price = None
        sentiment_direction = get_latest_sentiment_direction(sentiment_log_path)

        if sentiment_direction:
            print(f"📊 Latest sentiment direction: {sentiment_direction}")
            if sentiment_direction == "drop" and direction == "long":
                proposed_sl = entry_price * (1 - tight_sl_percent_long / leverage)
                if proposed_sl >= last_price:
                    print("⚠️ Sentiment SL (from entry) is above market price. Recalculating from market price.")
                    new_sl_price = last_price * (1 - tight_sl_percent_long / leverage)
                else:
                    new_sl_price = proposed_sl
                tight_sl_override = True
                print(f"🔒 Tight SL (sentiment DROP) for LONG set to: {new_sl_price:.{decimals}f}")

            elif sentiment_direction == "rise" and direction == "short":
                proposed_sl = entry_price * (1 + tight_sl_percent_short / leverage)
                if proposed_sl <= last_price:
                    print("⚠️ Sentiment SL (from entry) is below market price. Recalculating from market price.")
                    new_sl_price = last_price * (1 + tight_sl_percent_short / leverage)
                else:
                    new_sl_price = proposed_sl
                tight_sl_override = True
                print(f"🔒 Tight SL (sentiment RISE) for SHORT set to: {new_sl_price:.{decimals}f}")

        # Jos ei sentimenttipohjaista overridea, käytetään normaalia SL-logiikkaa
        if tight_sl_override:
            print("✅ Using tight sentiment-based SL override.")
        else:
            if excessive_sl:
                print(f"⚠️ Existing SL is too far ({stop_loss}), using 'excessive_stop_loss_percent'.")
                if direction == "long":
                    new_sl_price = entry_price - (entry_price * excessive_sl_percent)
                    if new_sl_price >= last_price:
                        print(f"❌ New SL {new_sl_price:.{decimals}f} is above market price {last_price:.{decimals}f}, skipping update.")
                        return []
                else:
                    new_sl_price = entry_price + (entry_price * excessive_sl_percent)
                    if new_sl_price <= last_price:
                        print(f"❌ New SL {new_sl_price:.{decimals}f} is below market price {last_price:.{decimals}f}, skipping update.")
                        return []
            elif missing_sl:
                new_sl_price = excessive_sl
                print("⚠️ SL missing, setting default excessive SL.")

        # 🔒 Jos SL edelleen puuttuu (esim. kaikki ehdot epäonnistuivat)
        if new_sl_price is None:
            print("❌ Could not determine new SL price, skipping update.")
            return []

        # ⚠️ Varmistetaan ettei SL ole väärällä puolella
        if direction == "long" and new_sl_price >= last_price:
            print(f"❌ New SL {new_sl_price:.{decimals}f} is above market price {last_price:.{decimals}f}, skipping update.")
            return []
        elif direction == "short" and new_sl_price <= last_price:
            print(f"❌ New SL {new_sl_price:.{decimals}f} is below market price {last_price:.{decimals}f}, skipping update.")
            return []

        if abs(stop_loss - new_sl_price) < 10 ** -decimals and not tight_sl_override:
            print(f"⏩ New SL {new_sl_price:.{decimals}f} is the same as existing SL {stop_loss:.{decimals}f}, skipping update.")
            return []
        elif abs(stop_loss - new_sl_price) < 10 ** -decimals and tight_sl_override:
            print(f"🔁 Sentiment-based override even though SL is same. Proceeding with update.")

        # ⛔ Estetään SL:n huononnus (isompi tappio)
        if direction == "long" and stop_loss > 0 and new_sl_price < stop_loss:
            print(f"❌ Existing SL {stop_loss:.{decimals}f} is tighter than proposed {new_sl_price:.{decimals}f}, skipping update.")
            return []
        elif direction == "short" and stop_loss > 0 and new_sl_price > stop_loss:
            print(f"❌ Existing SL {stop_loss:.{decimals}f} is tighter than proposed {new_sl_price:.{decimals}f}, skipping update.")
            return []

        # ✅ SL päivitys
        new_sl_str = f"{new_sl_price:.{decimals}f}"
        body = {
            "category": "linear",
            "symbol": symbol,
            "stopLoss": new_sl_str,
            "slTriggerBy": "LastPrice",
            "tpslMode": "Full",
            "positionIdx": position_idx
        }

        try:
            print(f"📤 Updating SL to: {body}")
            response = client.set_trading_stop(**body)
            print(f"✅ SL updated: {response}")
        except Exception as e:
            print(f"[ERROR] Failed to update SL: {e}")

import json

def get_latest_sentiment_direction(log_path):
    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
        if not lines:
            return None
        last_entry = json.loads(lines[-1])
        return last_entry.get("trend_shift", {}).get("direction")
    except Exception as e:
        print(f"[ERROR] Failed to read sentiment log: {e}")
        return None