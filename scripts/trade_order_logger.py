# scripts/trade_order_logger.py

import json
import os
from datetime import datetime
from configs.config import (
    TRADE_LOG_FILE, TIMEZONE,
    BUY_FIRST_STOP_LOSS_PERCENT, BUY_SET_STOP_LOSS_PERCENT, BUY_TRAILING_STOP_LOSS_PERCENT, BUY_CLOSE_ORDER_LIMIT,
    SELL_FIRST_STOP_LOSS_PERCENT, SELL_SET_STOP_LOSS_PERCENT, SELL_TRAILING_STOP_LOSS_PERCENT, SELL_CLOSE_ORDER_LIMIT,
)

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

    if symbol not in log:
        log[symbol] = {"long": [], "short": []}

    direction_lower = direction.lower()

    if direction_lower == "long":
        first_sl = price * (1 + BUY_FIRST_STOP_LOSS_PERCENT * leverage)
        set_sl = price * (1 + BUY_SET_STOP_LOSS_PERCENT * leverage)
        trailing_sl_percent = BUY_TRAILING_STOP_LOSS_PERCENT  # ei skaalata
        close_order_limit = price * BUY_CLOSE_ORDER_LIMIT
        prefer = max  # korkeammat longissa
    elif direction_lower == "short":
        first_sl = price * (1 - SELL_FIRST_STOP_LOSS_PERCENT * leverage)
        set_sl = price * (1 - SELL_SET_STOP_LOSS_PERCENT * leverage)
        trailing_sl_percent = -SELL_TRAILING_STOP_LOSS_PERCENT  # ei skaalata
        close_order_limit = price * SELL_CLOSE_ORDER_LIMIT
        prefer = min  # matalammat shortissa
    else:
        raise ValueError("Direction must be 'long' or 'short'")

    # Uusi tilaus
    new_order = {
        "timestamp": now,
        "qty": qty,
        "price": price,
        "leverage": leverage,
        "first_stop_loss_price": round(first_sl, 8),
        "set_stop_loss_price": round(set_sl, 8),
        "trailing_stop_loss_percent": trailing_sl_percent,
        "close_order_limit": round(close_order_limit, 8)
    }

    existing_orders = log[symbol][direction_lower]

    if existing_orders:
        combined = existing_orders[0]
        combined["qty"] += new_order["qty"]
        combined["price"] = prefer(combined["price"], new_order["price"])
        combined["first_stop_loss_price"] = prefer(combined["first_stop_loss_price"], new_order["first_stop_loss_price"])
        combined["set_stop_loss_price"] = prefer(combined["set_stop_loss_price"], new_order["set_stop_loss_price"])
        combined["close_order_limit"] = prefer(combined.get("close_order_limit", new_order["close_order_limit"]), new_order["close_order_limit"])
        combined["timestamp"] = max(combined["timestamp"], new_order["timestamp"])  # uusin aika voittaa
    else:
        log[symbol][direction_lower].append(new_order)

    save_trade_log(log)
