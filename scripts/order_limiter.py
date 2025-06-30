# scripts/order_limiter.py
import json
from collections import defaultdict

def normalize_symbol(symbol):
    return symbol.replace("USDC", "USDT")

def load_initiated_orders(log_path="logs/order_log.json"):
    try:
        with open(log_path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

    initiated_counts = defaultdict(int)  # key: (normalized_symbol, direction)

    for symbol, directions in data.items():
        norm_symbol = normalize_symbol(symbol)
        for direction, orders in directions.items():
            for order in orders:
                if order.get("status") == "initated":
                    initiated_counts[(norm_symbol, direction)] += 1

    return initiated_counts

def can_initiate(symbol, direction, initiated_counts, all_symbols=None):

    norm_symbol = normalize_symbol(symbol)
    current_count = initiated_counts.get((norm_symbol, direction), 0)

    # Laske määrät kaikille symboleille molemmissa suunnissa
    counts_by_direction = {
        "long": [],
        "short": []
    }
    for dir_ in counts_by_direction.keys():
        # Täytä symbolikohtaiset määrät, nollilla jos ei löydy
        for s in all_symbols:
            ns = normalize_symbol(s)
            counts_by_direction[dir_].append(initiated_counts.get((ns, dir_), 0))

    # Etsi minimit kummassakin suunnassa
    min_long = min(counts_by_direction["long"]) if counts_by_direction["long"] else 0
    min_short = min(counts_by_direction["short"]) if counts_by_direction["short"] else 0

    # Tarkista onko symbolin count sama kuin minimi kyseisessä suunnassa
    # Long- ja short-aloituksia verrataan omiin minimeihinsä
    if direction == "long":
        return current_count == min_long
    else:  # direction == "short"
        return current_count == min_short
