# scripts/process_stop_loss_logic.py
import os
import json

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
        print(f"➡️  Size: {size}, Entry: {entry_price}, Leverage: {leverage}, Trailing: {trailing_stop}, "
              f"Set stop loss percent: {formatted['set']}, Partial stop loss percent: {formatted['partial']}, "
              f"Trailing stop loss percent: {formatted['trailing']}")
    else:
        print(f"➡️  Size: {size}, Entry: {entry_price}, Leverage: {leverage}, Trailing: {trailing_stop}, "
              f"Set stop loss percent: {set_sl_percent}, Partial stop loss percent: {partial_sl_percent}, "
              f"Trailing stop loss percent: {trailing_percent}")



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
