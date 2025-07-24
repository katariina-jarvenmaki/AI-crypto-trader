from scripts.min_buy_calc import calculate_minimum_valid_bybit_purchase
from integrations.bybit_api_client import (
    place_leveraged_bybit_order,
    get_available_balance,
    get_bybit_symbol_info,
    client as bybit_client
)
from configs.config import leverage_map, default_leverage
from integrations.bybit_api_client import place_leveraged_bybit_limit_order

def execute_bybit_short_limit(symbol, risk_strength, current_equity, minimum_investment, min_inv_diff_percent):
    if risk_strength != "strong":
        return None

    bybit_symbol = symbol.replace("USDC", "USDT")
    leverage = leverage_map.get(bybit_symbol, default_leverage)

    result = calculate_minimum_valid_bybit_purchase(bybit_symbol)
    if not result:
        print(f"❌ Failed to calculate minimum purchase for Bybit symbol {bybit_symbol}")
        return None

    # Optionally increase qty if min_inv_diff_percent > 0
    qty = result["qty"]
    if min_inv_diff_percent > 0:
        original_qty = result["qty"]
        increased_qty = original_qty * (1 + min_inv_diff_percent / 100)
        # Round up if needed or keep same precision
        qty = max(original_qty, increased_qty)
        
    balance = get_available_balance("USDT")
    cost_with_leverage = result["cost"] / leverage
    if balance < cost_with_leverage:
        print(f"❌ Insufficient balance: {balance} < {cost_with_leverage}")
        return None

    print(f"📦 Bybit LIMIT SHORT order: {bybit_symbol} {result['qty']} units @ {result['price']} USDT")

    order_result = place_leveraged_bybit_limit_order(
        client=bybit_client,
        symbol=bybit_symbol,
        qty=qty,
        price=result["price"],
        leverage=leverage,
        side="Sell"
    )

    if order_result:
        print(f"✅ Bybit LIMIT SHORT trade placed: TP @ {order_result['tp_price']}, SL @ {order_result['sl_price']}")
        return {
            "symbol": bybit_symbol,
            "direction": "short",
            "qty": qty,
            "price": result["price"],
            "cost": result["cost"],
            "leverage": leverage,
            "tp_price": order_result["tp_price"],
            "sl_price": order_result["sl_price"]
        }
    else:
        print(f"❌ Failed to place Bybit LIMIT SHORT trade for symbol {bybit_symbol}")
        return None
