import json
import os
from datetime import datetime
from configs.config import TRADE_LOG_FILE, TIMEZONE
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOG_PATH = os.path.join(BASE_DIR, "logs", "order_log.json")

def safe_load_json(filepath):
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            f.write("{}")
        return {}

    try:
        with open(filepath, 'r') as f:
            content = f.read().strip()
            if not content:
                with open(filepath, 'w') as f_write:
                    f_write.write("{}")
                return {}
            return json.loads(content)
    except json.JSONDecodeError:
        with open(filepath, 'w') as f:
            f.write("{}")
        return {}

def load_trade_log():
    # Käytetään turvallista latausta
    return safe_load_json(TRADE_LOG_FILE)

def save_trade_log(log):
    with open(TRADE_LOG_FILE, "w") as f:
        json.dump(log, f, indent=4)

def log_trade(symbol: str, direction: str, qty: float, price: float, cost: float, leverage: int,
              order_take_profit: float = None, order_stop_loss: float = None,
              interval: str = None, mode: str = "default", market_state: str = None,
              started_on: str = None, momentum_strength: str = None,
              price_change: str = None, volume_multiplier: float = None,
              reverse_signal_info: dict = None, platform: dict = None):

    print(f"[log_trade] Logging {symbol} {direction} {qty} @ {price} on {platform}")

    log = load_trade_log()
    now = datetime.now(TIMEZONE).isoformat()

    if symbol not in log:
        log[symbol] = {"long": [], "short": []}

    direction_lower = direction.lower()

    new_order = {
        "timestamp": now,
        "platform": platform,
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
        "reverse_strength": reverse_signal_info.get("momentum_strength") if reverse_signal_info else None,
        "volume_multiplier": volume_multiplier,
        "price_change": price_change,
        "market_state": market_state,
        "started_on": started_on   
    }

    log[symbol][direction_lower].append(new_order)

    save_trade_log(log)

def load_trade_logs(status_filter=None, platform=None, filepath=LOG_PATH):
    data = safe_load_json(filepath)

    results = []
    for symbol, positions in data.items():
        for direction in ['long', 'short']:
            for order in positions.get(direction, []):
                if status_filter and order.get("status") != status_filter:
                    continue
                if platform and order.get("platform") != platform:
                    continue
                order_entry = {
                    "symbol": symbol,
                    "direction": direction,
                    **order
                }
                results.append(order_entry)
    return results

def update_order_status(order_id, new_status, filepath=LOG_PATH):
    data = safe_load_json(filepath)

    updated = False
    for symbol_orders in data.values():
        for direction_orders in symbol_orders.values():
            for order in direction_orders:
                if str(order.get("timestamp")) == str(order_id):
                    order["status"] = new_status
                    updated = True

    if updated:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    return updated
