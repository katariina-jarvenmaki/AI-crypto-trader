# trade/execute_bybit_long.py

from scripts.min_buy_calc import calculate_minimum_valid_bybit_purchase
from integrations.bybit_api_client import (
    place_leveraged_bybit_order,
    get_available_balance,
    get_bybit_symbol_info,
    client as bybit_client
)
from configs.config import leverage_map, default_leverage

def execute_bybit_long(symbol, risk_strength):

    # Only proceed if the risk level is strong
    if risk_strength != "strong":
        return None

    # Convert USDC to USDT in symbol name if needed
    bybit_symbol = symbol.replace("USDC", "USDT")

    # Calculate minimum valid purchase size
    result = calculate_minimum_valid_bybit_purchase(bybit_symbol)
    if not result:
        print(f"❌ Failed to calculate minimum purchase for Bybit symbol {bybit_symbol}")
        return None

    # Check if there is enough available balance
    balance = get_available_balance("USDT")
    if balance < result["cost"]:
        print(f"❌ Insufficient balance: {balance} < {result['cost']}")
        return None

    print(f"📦 Bybit minimum order: {bybit_symbol} {result['qty']} units @ {result['price']} USD → total {result['cost']} USD")

    # Determine leverage from config or use default
    leverage = leverage_map.get(bybit_symbol, default_leverage)

    # Place leveraged order
    order_result = place_leveraged_bybit_order(
        client=bybit_client,
        symbol=bybit_symbol,
        qty=result["qty"],
        price=result["price"],
        leverage=leverage
    )

    if order_result:
        print(f"✅ Bybit trade executed: TP @ {order_result['tp_price']}, SL @ {order_result['sl_price']}")
        return {
            "symbol": bybit_symbol,
            "direction": "long",
            "qty": result["qty"],
            "price": result["price"],
            "leverage": leverage,
            "tp_price": order_result["tp_price"],
            "sl_price": order_result["sl_price"]
        }
    else:
        print(f"❌ Failed to execute Bybit trade for symbol {bybit_symbol}")
        return None