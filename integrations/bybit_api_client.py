# integrations/bybit_api_client.py

from pybit.unified_trading import HTTP
import pandas as pd
import sys
import os
import math

# Polut ja konfiguraatiot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configs.credentials import BYBIT_API_KEY, BYBIT_API_SECRET
from configs.bybit_config import BYBIT_INTERVALS

# Bybit V5 unified trading client
client = HTTP(
    api_key=BYBIT_API_KEY, 
    api_secret=BYBIT_API_SECRET, 
    testnet=False
)

# --- Asetukset ---
DEFAULT_LEVERAGE = 2
CATEGORY = "linear"  # Käytetään vivullista perpetual-kauppaa
TP_MULTIPLIER = 1.3  # +30%
SL_MULTIPLIER = 0.9  # -10%

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
def get_bybit_price(symbol: str):
    try:
        response = client.get_tickers(category=CATEGORY, symbol=symbol)
        return float(response["result"]["list"][0]["lastPrice"])
    except Exception as e:
        print(f"❌ Bybitin hintahaku epäonnistui: {e}")
        return None

def get_available_balance(asset="USDT"):
    try:
        response = client.get_wallet_balance(accountType="UNIFIED")
        coins = response["result"]["list"][0]["coin"]

        for coin in coins:
            if coin["coin"] == asset:
                # Joustavasti haetaan joko availableToTrade, availableBalance tai equity
                return float(
                    coin.get("availableToTrade") or
                    coin.get("availableBalance") or
                    coin.get("equity") or 0.0
                )

        return 0.0
    except Exception as e:
        print(f"⚠️ Saldohaun virhe: {str(e)}")
        return 0.0

def place_leveraged_bybit_order(symbol: str, qty: float, price: float, leverage: int = DEFAULT_LEVERAGE):
    try:
        # Aseta hedge mode ennen mitään muuta
        set_hedge_mode(symbol=symbol, category=CATEGORY)

        # Aseta vipu
        set_leverage(symbol, leverage)

        # Pyöristä määrä
        rounded_qty = round_bybit_quantity(symbol, qty)

        # Suorita ostotoimeksianto
        buy_order = client.place_order(
            category=CATEGORY,
            symbol=symbol,
            side="Buy",
            orderType="Market",
            qty=str(rounded_qty),
            isLeverage=1
        )

        # Laske TP/SL
        tp_price = round(price * TP_MULTIPLIER, 2)
        sl_price = round(price * SL_MULTIPLIER, 2)

        return {
            "tp_price": tp_price,
            "sl_price": sl_price,
            "buy_order": buy_order
        }

    except Exception as e:
        print(f"❌ Bybit leveraged order failed: {e}")
        return None

def get_bybit_symbol_info(symbol: str):
    try:
        response = client.get_instruments_info(category=CATEGORY, symbol=symbol)
        if response and "result" in response and "list" in response["result"]:
            return response["result"]["list"][0]
        else:
            print(f"⚠️ Ei saatu symbolitietoja Bybitiltä: {symbol}")
            return None
    except Exception as e:
        print(f"❌ Virhe Bybit-symbolitiedon haussa: {e}")
        return None

# --- Symbolikohtainen määrän pyöristys Bybit-kaupoissa ---
BYBIT_QUANTITY_ROUNDING = {
    "HBARUSDT": 0,
    "ETHUSDT": 2,
    "BTCUSDT": 3
}

def set_leverage(symbol: str, leverage: int, category: str = "linear"):
    try:
        if category == "linear":  # Futures / Perpetuals
            response = client.set_leverage(
                category="linear",
                symbol=symbol,
                buyLeverage=leverage,
                sellLeverage=leverage,
            )
            print(f"✅ Vipu asetettu: {symbol} @ {leverage}x → {response}")
        elif category == "spot_margin":
            response = client.spot_margin_trade_set_leverage(
                leverage=str(leverage)
            )
            print(f"✅ Spot-margin vipu asetettu: {symbol} @ {leverage}x → {response}")
        else:
            print(f"⚠️ Tuntematon kategoria: {category}")
    except Exception as e:
        print(f"❌ Vivun asetus epäonnistui: {e}")

def round_bybit_quantity(symbol: str, qty: float) -> float:
    info = get_bybit_symbol_info(symbol)
    if info and "lotSizeFilter" in info:
        step_size = float(info["lotSizeFilter"]["qtyStep"])
        precision = abs(int(round(-math.log10(step_size))))
        return round(qty, precision)
    # fallback
    decimals = BYBIT_QUANTITY_ROUNDING.get(symbol.upper(), 4)
    return round(qty, decimals)

def set_hedge_mode(symbol: str, category: str = "linear"):
    try:
        # Tarkista onko mitään positioita auki — jos on, ei voi vaihtaa tilaa
        response = client.get_positions(category=category, symbol=symbol)
        positions = response.get("result", {}).get("list", [])

        open_position_exists = any(
            float(pos.get("size", 0)) > 0 for pos in positions
        )

        if open_position_exists:
            print(f"⚠️ Hedge-modea ei voida vaihtaa, koska avoimia positioita on jo olemassa.")
            return

        # Asetetaan hedge-mode koko tilille
        response = client.switch_position_mode(
            category=category,
            symbol=symbol.upper(),
            mode=3  # Hedge Mode
        )
        print(f"✅ Hedge-tila asetettu: {response}")
    except Exception as e:
        print(f"❌ Position mode -asetuksen virhe: {e}")


def has_open_position(symbol: str, category: str = "linear") -> bool:
    try:
        response = client.get_positions(category=category, symbol=symbol)
        positions = response.get("result", {}).get("list", [])
        for pos in positions:
            if float(pos.get("size", 0)) > 0:
                return True
        return False
    except Exception as e:
        print(f"⚠️ Positioiden tarkistus epäonnistui: {e}")
        return False

# --- Testaus ---
if __name__ == "__main__":
    print("✅ Bybit Leverage API Integration Test")

    test_symbol = "BTCUSDT"
    try:
        price = get_bybit_price(test_symbol)
        if price:
            print(f"✅ Price fetch for {test_symbol}: OK (Current price: {price})")
        else:
            print(f"❌ ERROR: Failed to fetch price for {test_symbol}")
    except Exception as e:
        print(f"❌ ERROR during price fetch: {e}")