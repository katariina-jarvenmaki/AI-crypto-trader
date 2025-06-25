# scripts/spot_order_handler.py

from integrations.binance_api_client import client
from integrations.binance_api_client import get_current_price
import math

def round_price(price, tick_size):
    precision = int(round(-math.log10(tick_size), 0))
    return round(price, precision)

def place_spot_trade_with_tp_sl(symbol, qty, entry_price, tick_size):
    try:
        # ✅ Osto (MARKET)
        print(f"📥 Placing MARKET BUY for {symbol} - Qty: {qty}")
        buy_order = client.create_order(
            symbol=symbol,
            side='BUY',
            type='MARKET',
            quantity=qty
        )

        # ⬆️ Take Profit
        tp_price = round_price(entry_price * 1.01, tick_size)
        print(f"🎯 Setting TAKE PROFIT @ {tp_price}")
        client.create_order(
            symbol=symbol,
            side='SELL',
            type='LIMIT',
            timeInForce='GTC',
            quantity=qty,
            price=str(tp_price)
        )

        # ⬇️ Stop Loss
        sl_price = round_price(entry_price * 0.90, tick_size)
        print(f"🛑 Setting STOP LOSS @ {sl_price}")
        client.create_order(
            symbol=symbol,
            side='SELL',
            type='STOP_LOSS_LIMIT',
            timeInForce='GTC',
            quantity=qty,
            stopPrice=str(sl_price),
            price=str(sl_price)
        )

        return {
            "buy_order": buy_order,
            "tp_price": tp_price,
            "sl_price": sl_price
        }

    except Exception as e:
        print(f"❌ Trade execution failed: {e}")
        return None
