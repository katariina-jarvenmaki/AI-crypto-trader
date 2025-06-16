# integrations/bybit_api_client.py

from pybit.unified_trading import HTTP
import pandas as pd
import sys
import os

# Polut ja konfiguraatiot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configs.credentials import BYBIT_API_KEY, BYBIT_API_SECRET
from configs.bybit_config import BYBIT_INTERVALS

# Bybit V5 unified trading client
client = HTTP(api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)

# --- Asetukset ---
DEFAULT_LEVERAGE = 1
CATEGORY = "linear"  # Käytetään vivullista perpetual-kauppaa
TP_MULTIPLIER = 1.02  # +2%
SL_MULTIPLIER = 0.97  # -3%

# --- OHLCV yhdelle symbolille ja usealle aikavälille ---
def fetch_ohlcv_for_intervals(symbol: str, intervals: list, limit: int = 100):
    result = {}
    for interval in intervals:
        try:
            response = client.get_kline(category=CATEGORY, symbol=symbol, interval=interval, limit=limit)
            data = response['result']['list']
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df.astype(float)
            result[interval] = df
        except Exception as e:
            print(f"⚠️ OHLCV fetch error for {symbol} - {interval}: {e}")
    return result

# --- OHLCV useille symboleille ja intervalleille ---
def fetch_multi_ohlcv(selected_symbols: list, limit=100):
    result = {}
    for symbol in selected_symbols:
        result[symbol] = fetch_ohlcv_for_intervals(symbol, BYBIT_INTERVALS, limit)
    return result

# --- Reaaliaikaiset hinnat ---
def get_all_current_prices(selected_symbols: list):
    try:
        response = client.get_tickers(category=CATEGORY)
        prices = {
            item["symbol"]: float(item["lastPrice"])
            for item in response["result"]["list"]
            if item["symbol"] in selected_symbols
        }
        return prices
    except Exception as e:
        print(f"❌ Hintojen massahaku epäonnistui: {e}")
        return {}

# --- Yksittäinen hinta ---
def get_current_price(symbol: str):
    try:
        response = client.get_tickers(category=CATEGORY, symbol=symbol)
        return float(response["result"]["list"][0]["lastPrice"])
    except Exception as e:
        print(f"❌ Hintahaku epäonnistui: {e}")
        return None

# --- Markkinatoimeksianto vivulla ---
def place_market_order(symbol: str, side: str, quantity: float, leverage: int = DEFAULT_LEVERAGE):
    try:
        # Aseta vivutus (tarvittaessa vain kerran per symboli)
        client.set_leverage(category=CATEGORY, symbol=symbol, buyLeverage=leverage, sellLeverage=leverage)

        return client.place_order(
            category=CATEGORY,
            symbol=symbol,
            side=side.upper(),  # "BUY" tai "SELL"
            orderType="Market",
            qty=str(quantity)
        )
    except Exception as e:
        print(f"❌ Market order with leverage failed: {e}")
        return None

# --- Limittitoimeksianto vivulla ---
def place_limit_order(symbol: str, side: str, quantity: float, price: float, leverage: int = DEFAULT_LEVERAGE):
    try:
        client.set_leverage(category=CATEGORY, symbol=symbol, buyLeverage=leverage, sellLeverage=leverage)

        return client.place_order(
            category=CATEGORY,
            symbol=symbol,
            side=side.upper(),
            orderType="Limit",
            qty=str(quantity),
            price=str(price),
            timeInForce="GTC"
        )
    except Exception as e:
        print(f"❌ Limit order with leverage failed: {e}")
        return None

# --- Testaus ---
if __name__ == "__main__":
    print("✅ Bybit Leverage API Integration Test")

    test_symbol = "BTCUSDT"

    try:
        price = get_current_price(test_symbol)
        if price:
            print(f"✅ Price fetch for {test_symbol}: OK (Current price: {price})")
        else:
            print(f"❌ ERROR: Failed to fetch price for {test_symbol}")
    except Exception as e:
        print(f"❌ ERROR during price fetch: {e}")

    try:
        account_info = client.get_wallet_balance(accountType="UNIFIED")
        if "result" in account_info:
            print("✅ Account access (API key permissions): OK")
        else:
            print("❌ ERROR: Unexpected account info response.")
    except Exception as e:
        print(f"❌ ERROR during account info check: {e}")

def place_leveraged_bybit_order(symbol: str, qty: float, price: float):
    try:
        # Aseta ostotoimeksianto (BUY)
        buy_order = place_limit_order(symbol=symbol, side="Buy", quantity=qty, price=price)
        if not buy_order:
            return None

        # Laske TP ja SL hinnat
        tp_price = round(price * TP_MULTIPLIER, 2)
        sl_price = round(price * SL_MULTIPLIER, 2)

        # Voit halutessasi asettaa TP/SL erikseen, esim. käyttämällä `take_profit` ja `stop_loss` kenttiä
        return {
            "tp_price": tp_price,
            "sl_price": sl_price,
            "buy_order": buy_order
        }
    except Exception as e:
        print(f"❌ Bybit leveraged order failed: {e}")
        return None