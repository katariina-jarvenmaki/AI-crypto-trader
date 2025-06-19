# scripts/trade_order_logger.py
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

def log_trade(symbol: str, direction: str, qty: float, price: float, leverage: int):
    log = load_trade_log()
    now = datetime.now(TIMEZONE).isoformat()

    # Alusta tarvittavat rakenteet
    if symbol not in log:
        log[symbol] = {"long": [], "short": []}

    order_data = {
        "timestamp": now,
        "qty": qty,
        "price": price,
        "leverage": leverage,
        "first_stop_loss_price": None,
        "set_stop_loss_price": None
    }

    if direction.lower() not in ["long", "short"]:
        raise ValueError("Direction must be 'long' or 'short'")

    log[symbol][direction.lower()].append(order_data)
    save_trade_log(log)
