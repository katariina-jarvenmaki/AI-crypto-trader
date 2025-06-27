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

def log_trade(symbol: str, direction: str, qty: float, price: float, leverage: int,
              order_take_profit: float, order_stop_loss: float):
    log = load_trade_log()
    now = datetime.now(TIMEZONE).isoformat()

    if symbol not in log:
        log[symbol] = {"long": [], "short": []}

    direction_lower = direction.lower()

    new_order = {
        "timestamp": now,
        "qty": qty,
        "price": price,
        "leverage": leverage,
        "order_take_profit_price": order_take_profit,
        "order_stop_loss_price": order_stop_loss
    }

    log[symbol][direction_lower].append(new_order)

    save_trade_log(log)