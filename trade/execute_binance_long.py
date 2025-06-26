# trade/execute_binance_long.py

from scripts.min_buy_calc import calculate_minimum_valid_purchase
from scripts.spot_order_handler import place_spot_trade_with_tp_sl

def execute_binance_long(symbol, risk_strength):

    # Only proceed if the risk level is strong
    if risk_strength != "strong":
        return

    result = calculate_minimum_valid_purchase(symbol)
    if not result:
        print(f"❌ Binance minimum purchase calculation failed for symbol {symbol}")
        return

    quantity = "{:.8f}".format(result['qty'])
    # print(f"✅ Binance minimum purchase: {symbol} {quantity} units @ {result['price']:.4f} → total {result['cost']:.2f} USD")

    # Place spot trade with take-profit and stop-loss
    order_result = place_spot_trade_with_tp_sl(
        symbol, 
        quantity, 
        result["price"], 
        result["step_size"]
    )
    if order_result:
        print(f"✅ TP/SL set: TP @ {order_result['tp_price']}, SL @ {order_result['sl_price']}")
    else:
        if order_result and "error" not in order_result:
            print(f"✅ TP/SL set: TP @ {order_result['tp_price']}, SL @ {order_result['sl_price']}")
        else:
            error_msg = order_result.get("error", "Unknown error") if order_result else "Unknown error"
            print(f"❌ Binance trade failed for symbol {symbol}: {error_msg}")
