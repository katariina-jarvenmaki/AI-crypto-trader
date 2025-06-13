# integrations/binance_api_client.py

from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
import pandas as pd
import sys
import os

# Paths, confs and credentials
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configs.credentials import BINANCE_API_KEY, BINANCE_API_SECRET
from configs.binance_config import BINANCE_INTERVALS

client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)

### --- OHLCV for multible symbols and intervals ---
def fetch_ohlcv_for_intervals(symbol: str, intervals: list, limit: int = 100):
    """Hakee OHLCV-datat yhdelle symbolille useilta aikaväleiltä."""
    result = {}
    for interval in intervals:
        try:
            klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
            ])
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df.astype(float)
            result[interval] = df
        except BinanceAPIException as e:
            print(f"⚠️ OHLCV fetch error for {symbol} - {interval}: {e.message}")
    return result

def fetch_multi_ohlcv(selected_symbol: list, limit=10):
    """Hakee OHLCV-dataa kaikille käyttäjän valitsemille symboleille ja konfiguroiduille intervalleille."""
    result = {}
    for symbol in selected_symbol:
        result[symbol] = {}
        for interval in BINANCE_INTERVALS:
            try:
                klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
                df = pd.DataFrame(klines, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_asset_volume', 'number_of_trades',
                    'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
                ])
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                df = df.astype(float)
                result[symbol][interval] = df
            except BinanceAPIException as e:
                print(f"⚠️ OHLCV fetch error {symbol} - {interval}: {e.message}")
    return result


### --- Get real prices for selected symbols ---
def get_all_current_prices(selected_symbol: list):
    """Hakee reaaliaikaiset hinnat kaikille valituille symboleille yhdellä kutsulla."""
    try:
        all_prices = client.get_all_tickers()
        return {p["symbol"]: float(p["price"]) for p in all_prices if p["symbol"] in selected_symbol}
    except BinanceAPIException as e:
        print(f"❌ Hintojen massahaku epäonnistui: {e.message}")
        return {}


### --- Spot Trading ---
def place_market_order(symbol: str, side: str, quantity: float):
    try:
        return client.create_order(
            symbol=symbol,
            side=SIDE_BUY if side.lower() == "buy" else SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )
    except BinanceAPIException as e:
        print(f"❌ API error: {e.message}")
        return None


def place_limit_order(symbol: str, side: str, quantity: float, price: float):
    try:
        return client.create_order(
            symbol=symbol,
            side=SIDE_BUY if side.lower() == "buy" else SIDE_SELL,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=quantity,
            price=str(price)
        )
    except BinanceAPIException as e:
        print(f"❌ API error: {e.message}")
        return None

### --- Single price search ---
def get_current_price(symbol: str):
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except BinanceAPIException as e:
        print(f"❌ Hintahaku epäonnistui: {e.message}")
        return None

if __name__ == "__main__":
    print("✅ Binance API Integration Test")

    # 1. Test connection
    try:
        client.ping()
        print("✅ Connection to Binance API: OK")
    except BinanceAPIException as e:
        print(f"❌ ERROR: Failed to connect to Binance API: {e.message}")
    except Exception as e:
        print(f"❌ ERROR: Unexpected issue with Binance connection: {e}")
    
    # 2. Test price
    test_symbol = "BTCUSDT"
    try:
        price = get_current_price(test_symbol)
        if price:
            print(f"✅ Price fetch for {test_symbol}: OK (Current price: {price})")
        else:
            print(f"❌ ERROR: Failed to fetch price for {test_symbol}")
    except Exception as e:
        print(f"❌ ERROR: Exception during price fetch: {e}")

    # 3. Test account info (API permissions)
    try:
        account_info = client.get_account()
        if "balances" in account_info:
            print("✅ Account access (API key permissions): OK")
            print("✅ Binance API integration seems to be working")
        else:
            print("❌ ERROR: Unexpected response in account info.")
    except BinanceAPIException as e:
        if "API-key format invalid" in str(e.message):
            print("❌ ERROR: Binance API keys invalid - check configs/credentials.py")
        elif "API-key does not have permission" in str(e.message):
            print("❌ ERROR: API key lacks required permissions (e.g. trading or account info)")
        else:
            print(f"❌ ERROR: Account access issue: {e.message}")

    except Exception as e:
        print(f"❌ ERROR: Unexpected error in account info check: {e}")
