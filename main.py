import sys
from scripts.platform_selection import get_selected_platform
from scripts.symbol_selection import get_selected_symbols
from scripts.binance_api_client import fetch_multi_ohlcv, get_all_current_prices

arg_list = sys.argv[1:]  # Komentoriviparametrit ilman tiedostonimeä

# 1. Platformin valinta
try:
    selected_platform = get_selected_platform(arg_list)
except ValueError as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

# 2. Symbolit ilman platform-parametria
symbol_args = arg_list[1:] if selected_platform.lower() == arg_list[0].lower() else arg_list

# 3. Symbolien valinta
try:
    selected_symbols = get_selected_symbols(selected_platform, symbol_args)
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

# 4. Tulostus
print(f"✅ Selected platform: {selected_platform}")
print(f"✅ Selected symbols: {selected_symbols}")

# 5. Esimerkki käyttö API-klientin kanssa (voit poistaa kommentit)
ohlcv_data = fetch_multi_ohlcv(selected_symbols, limit=20)
live_prices = get_all_current_prices(selected_symbols)
for symbol in selected_symbols:
    print(f"\n📊 {symbol} - Live price: {live_prices.get(symbol, 'N/A')}")
