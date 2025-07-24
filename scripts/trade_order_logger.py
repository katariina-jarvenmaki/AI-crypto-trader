import json
import os
from datetime import datetime
from configs.config import TRADE_LOG_FILE, TIMEZONE
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOG_PATH = os.path.join(BASE_DIR, "../AI-crypto-trader-logs/order-data/order_log.json")
SKIPPED_LOG_PATH = os.path.join(BASE_DIR, "../AI-crypto-trader-logs/order-data/skipped_orders.json")

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

def log_trade(symbol: str, direction: str, org_qty: float, qty: float, price: float, cost: float, leverage: int,
              order_take_profit: float = None, order_stop_loss: float = None,
              interval: str = None, rsi: str = None, mode: str = "default", market_state: str = None,
              started_on: str = None, momentum_strength: str = None,
              price_change: str = None, volume_multiplier: float = None,
              reverse_signal_info: dict = None, platform: dict = None, status=None, ohlcv_data=None, price_data=None, history_analysis_data=None, history_sentiment=None):
    print(f"[log_trade] Logging {symbol} {direction} {qty} @ {price} on {platform}")
                
    log = load_trade_log()
    now = datetime.now(TIMEZONE).isoformat()

    if symbol not in log:
        log[symbol] = {"long": [], "short": []}

    direction_lower = direction.lower()

    new_order = {
        "timestamp": now,
        "platform": platform,
        "status" : "initiated",
        "minium_qty": org_qty,
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
        "started_on": started_on,
        "ohlcv_data": ohlcv_data,
        "price_data": price_data,
        "history_analysis_data": history_analysis_data,
        "history_sentiment_data": history_sentiment
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

def update_order_status(order_timestamp, new_status, filepath=LOG_PATH):
    data = safe_load_json(filepath)
    updated = False
    for symbol, positions in data.items():
        for direction in ['long', 'short']:
            for order in positions.get(direction, []):
                if order.get("timestamp") == order_timestamp:
                    order["status"] = new_status
                    updated = True
                    break
            if updated:
                break
        if updated:
            break
    if updated:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
    return updated

def reactivate_completed_orders(filepath=LOG_PATH):
    data = safe_load_json(filepath)
    updated_any = False

    for symbol, positions in data.items():
        for direction in ['long', 'short']:
            orders = positions.get(direction, [])
            for order in orders:
                if order.get("status") == "completed":
                    order["status"] = "initiated"
                    updated_any = True
                    print(f"🔄 Re-activated completed order as initiated for {symbol} {direction}")

    if updated_any:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
    else:
        print("No completed orders to reactivate.")

    return updated_any

def log_skipped_order(symbol: str, reason: str, direction: str = None, details: dict = None, order_data: dict = None, history_sentiment: dict = None):
    filepath = SKIPPED_LOG_PATH.replace(".jsonl", ".json")

    now = datetime.now(TIMEZONE).isoformat()

    entry = {
        "timestamp": now,
        "symbol": symbol,
        "direction": direction,
        "platform": "ByBit",
        "status": "skipped",
        "skipped": True,
        "skipped_reason": reason,
        "qty": None,
        "price": None,
        "cost": None,
        "leverage": None,
        "order_take_profit_price": None,
        "order_stop_loss_price": None,
        "mode": "default",
        "interval": None,
        "momentum_strength": None,
        "reverse_strength": None,
        "volume_multiplier": None,
        "price_change": None,
        "market_state": None,
        "started_on": None,
        "ohlcv_data": None,
        "price_data": None,
        "history_analysis_data": None,
        "history_sentiment_data": None,
        "details": details or {}
    }

    # Täytetään tiedot mahdollisesta olemassa olevasta order_datasta
    if order_data:
        for key in entry.keys():
            if key in order_data:
                entry[key] = order_data[key]

    # Ladataan aiemmat tiedot
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                skipped_orders = json.load(f)
        except json.JSONDecodeError:
            skipped_orders = []
    else:
        skipped_orders = []

    entry["history_sentiment_data"] = history_sentiment

    skipped_orders.append(entry)

    with open(filepath, "w") as f:
        json.dump(skipped_orders, f, indent=4)

    print(f"[log_skipped_order] {symbol} {direction or ''} skipped: {reason}")
