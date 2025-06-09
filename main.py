# main.py

import sys
from scripts.platform_selection import get_selected_platform
from scripts.binance_interface import fetch_multi_ohlcv, get_all_current_prices

# Platform selection
try:
    selected_platform = get_selected_platform(sys.argv[1:])
except ValueError as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

# Haetaan OHLCV-data
# ohlcv = fetch_multi_ohlcv(selected_symbol, limit=20)

# Haetaan live-hinnat
# live_prices = get_all_current_prices(selected_platform)

# Tulostus
# for symbol in selected_platform:
#    print(f"\n📊 {symbol} - Hinta nyt: {live_prices.get(symbol, 'N/A')}")


# Printing to console
print(f"Selected platform: {selected_platform}")
print("Select coinpair")

