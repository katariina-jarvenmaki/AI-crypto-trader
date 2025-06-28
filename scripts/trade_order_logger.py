import json
import os
from datetime import datetime
from configs.config import TRADE_LOG_FILE, TIMEZONE

def load_trade_log():
    if os.path.exists(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE, "r") as f:
            try:
                data = json.load(f)
                if not isinstance(data, dict):
                    return {}
                return data
            except json.JSONDecodeError:
                return {}
    return {}

def save_trade_log(log):
    with open(TRADE_LOG_FILE, "w") as f:
        json.dump(log, f, indent=4)

def log_trade(symbol: str, direction: str, qty: float, price: float, cost: float, leverage: int,
              order_take_profit: float = None, order_stop_loss: float = None,
              interval: str = None, mode: str = "default", market_state: str = None,
              started_on: str = None, momentum_strength: str = None,
              price_change: str = None, volume_multiplier: float = None,
              reverse_signal_info: dict = None, platform: dict = None):

    print(f"[log_trade] Logging {symbol} {direction} {qty} @ {price} on {platform}")  # 👈 TÄMÄ TÄHÄN

    log = load_trade_log()
    now = datetime.now(TIMEZONE).isoformat()

    if symbol not in log:
        log[symbol] = {"long": [], "short": []}

    direction_lower = direction.lower()

    new_order = {
        "timestamp": now,
        "platform": now,
        "status" : "initated",
        "qty": qty,
        "price": price,
        "cost": cost,
        "leverage": leverage,
        "order_take_profit_price": order_take_profit,
        "order_stop_loss_price": order_stop_loss,
        "mode": mode,
        "interval": interval,
        "momentum_strength": momentum_strength,
        "reverse_strength": reverse_signal_info.get("momentum_strength"),
        "volume_multiplier": volume_multiplier,
        "price_change": price_change,
        "market_state": market_state,
        "started_on": started_on   
    }

    log[symbol][direction_lower].append(new_order)

    save_trade_log(log)
