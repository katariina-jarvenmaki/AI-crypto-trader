# scripts/filter_initiated_orders.py
from scripts.trade_order_logger import load_trade_logs, update_order_status, safe_load_json

def filter_initiated_orders(orders, position_side):
    """
    orders: lista ordereista dict
    position_side: "Buy" tai "Sell"
    Palauttaa päivitetyn listan ja merkkaa ylimääräiset completeksi.
    """

    # Suodata initiated-tilaiset
    initiated_orders = [o for o in orders if o.get("status") == "initiated"]

    if len(initiated_orders) <= 1:
        # Ei ylimääräisiä initiatedeja, ei muutoksia
        return orders, False

    # Valitaan pidettävä orderi
    if position_side.lower() == "buy":  # long
        # Korkein hinta
        chosen = max(initiated_orders, key=lambda x: x.get("price", 0))
    else:  # "sell" / short
        # Matalin hinta
        chosen = min(initiated_orders, key=lambda x: x.get("price", float('inf')))

    updated_any = False
    for order in initiated_orders:
        if order != chosen:
            # Merkitse completeksi
            updated = update_order_status(order.get("timestamp"), "completed")
            if updated:
                updated_any = True
                order["status"] = "completed"  # päivitetään myös tässä listassa
                print(f"Marked order {order.get('timestamp')} as complete due to multiple initiated orders.")

    return orders, updated_any
