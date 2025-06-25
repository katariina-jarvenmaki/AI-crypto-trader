# scripts/bybit_order.py

from pybit.unified_trading import HTTP
import time

# Replace with your own testnet API credentials
api_key = "YE1YHtyIQQsMgfwNoo"
api_secret = "ZYTnRkxD60QcQVRrh1lHRflsMX9c8DipMefe"

# Create a session
session = HTTP(
    testnet=False,
    api_key=api_key,
    api_secret=api_secret,
)

# Optional: Set leverage (only for margin trading)
set_leverage_response = session.spot_margin_trade_set_leverage(
    leverage="7"  # You can choose between 2 and 10
)
print("Set Leverage Response:", set_leverage_response)

# Delay (optional but safe)
time.sleep(1)

# Place a Spot Limit Order
response = session.place_order(
    category="spot",
    symbol="BTCUSDT",
    side="Buy",
    orderType="Market",
    qty="105",  # in USDT (quote currency)
    timeInForce="IOC",
    orderLinkId="live-order-test-001",
    isLeverage=1,  # important: 1 means margin trade
    orderFilter="Order"
)

print("Order Response:", response)

