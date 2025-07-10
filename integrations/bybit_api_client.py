# integrations/bybit_api_client.py

from pybit.unified_trading import HTTP
import pandas as pd
import sys
import os
import math

# Polut ja konfiguraatiot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configs.credentials import BYBIT_API_KEY, BYBIT_API_SECRET
from configs.bybit_config import  (
    BYBIT_INTERVALS,
    DEFAULT_BYBIT_TAKE_PROFIT_PERCENT,
    DEFAULT_BYBIT_STOP_LOSS_PERCENT
)

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
def get_bybit_symbol_price(symbol):
    try:
        response = client.get_tickers(category="linear", symbol=symbol)
        return float(response["result"]["list"][0]["lastPrice"])
    except Exception as e:
        print(f"❌ Failed to fetch price for {symbol}: {e}")
        return None

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

def place_leveraged_bybit_order(client, symbol: str, qty: float, price: float, leverage: int = DEFAULT_LEVERAGE, side: str = "Buy"):

    try:
        # Enable hedge mode and set correct leverage
        set_hedge_mode(client, symbol=symbol, coin="USDT", category="linear")
        set_leverage(symbol, leverage)

        # Round quantity to valid tick size
        rounded_qty = round_bybit_quantity(symbol, qty)

        # Position index: 1 for Buy (long), 2 for Sell (short)
        position_idx = 1 if side == "Buy" else 2

        # Place the market order
        order = client.place_order(
            category=CATEGORY,
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=str(rounded_qty),
            isLeverage=1,
            positionIdx=position_idx
        )

        # Adjust SL and TP percentages **relative to leverage**
        adjusted_tp_percent = DEFAULT_BYBIT_TAKE_PROFIT_PERCENT / leverage  # e.g. 2% / 3x = 0.66%
        adjusted_sl_percent = DEFAULT_BYBIT_STOP_LOSS_PERCENT / leverage    # e.g. 10% / 3x = 3.33%

        # Calculate TP and SL prices based on order direction
        if side == "Buy":
            tp_price = price * (1 + adjusted_tp_percent)
            sl_price = price * (1 - adjusted_sl_percent)
        else:  # Sell
            tp_price = price * (1 - adjusted_tp_percent)
            sl_price = price * (1 + adjusted_sl_percent)

        # Set the trading stop with calculated SL/TP
        client.set_trading_stop(
            category="linear",
            symbol=symbol,
            takeProfit=str(tp_price),
            stopLoss=str(sl_price),
            tpTriggerBy="MarkPrice",
            slTriggerBy="MarkPrice",
            tpslMode="Full",
            tpOrderType="Market",
            slOrderType="Market",
            positionIdx=position_idx
        )

        print(f"✅ Bybit trade executed: TP @ {tp_price}, SL @ {sl_price}")
        return {
            "tp_price": tp_price,
            "sl_price": sl_price,
            "order": order
        }

    except Exception as e:
        print(f"❌ Bybit leveraged order failed: {e}")
        return None

def place_leveraged_bybit_limit_order(client, symbol: str, qty: float, price: float, leverage: int = DEFAULT_LEVERAGE, side: str = "Buy"):
    try:
        set_hedge_mode(client, symbol=symbol, coin="USDT", category="linear")
        set_leverage(symbol, leverage)

        rounded_qty = round_bybit_quantity(symbol, qty)
        position_idx = 1 if side == "Buy" else 2

        order = client.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType="Limit",
            qty=str(rounded_qty),
            price=str(price),
            isLeverage=1,
            positionIdx=position_idx,
            timeInForce="PostOnly",  # Takaa ettei market fillaa
            reduceOnly=False
        )

        print(f"✅ Bybit LIMIT order placed!")
        return {
            "tp_price": None,
            "sl_price": None,
            "order": order
        }

    except Exception as e:
        print(f"❌ Bybit LIMIT order failed: {e}")
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

# Testattu ja toimii, jos vipua ei ole jo asetettu symbolille
def set_leverage(symbol: str, leverage: int, category: str = "linear"):
    
    try:
        # Tarkista nykyinen vipu ensin
        current_leverage = None
        response = client.get_positions(category=category, symbol=symbol)
        positions = response.get("result", {}).get("list", [])
        for pos in positions:
            if pos["symbol"] == symbol:
                current_leverage = float(pos.get("leverage", 0))
                break

        if current_leverage == leverage:
            # print(f"ℹ️ Leverage is already set to {leverage}x for {symbol}. No changes needed.")
            return

        # Asetetaan vivutus, jos eri
        if category == "linear":  # Futures / Perpetuals
            response = client.set_leverage(
                category="linear",
                symbol=symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage)
            )
            # print(f"✅ Vipu asetettu: {symbol} @ {leverage}x → {response}")
        elif category == "spot_margin":
            response = client.spot_margin_trade_set_leverage(
                leverage=str(leverage)
            )
            # print(f"✅ Spot-margin vipu asetettu: {symbol} @ {leverage}x → {response}")
        else:
            print(f"⚠️ Tuntematon kategoria vivun asetuksessa: {category}")
    except Exception as e:
        print(f"❌ Vivun asetus epäonnistui: {e}")

def round_bybit_quantity(symbol: str, qty: float) -> float:
    info = get_bybit_symbol_info(symbol)
    if info and "lotSizeFilter" in info:
        step_size = float(info["lotSizeFilter"]["qtyStep"])
        # Laske desimaalit step_sizen perusteella
        precision = abs(int(round(-math.log10(step_size))))
        
        # Kerro qty kymmenen potenssiin precision ja pyöristä ylöspäin
        multiplier = 10 ** precision
        rounded_qty = math.ceil(qty * multiplier) / multiplier
        
        # Lisätään 1 askel ylimääräistä tarkkuutta
        # eli pyöristetään vielä yhdellä desimaalilla tarkemmin ylöspäin:
        extra_precision = precision + 1
        multiplier_extra = 10 ** extra_precision
        rounded_qty = math.ceil(rounded_qty * multiplier_extra) / multiplier_extra
        
        return rounded_qty
    
    # fallback
    decimals = BYBIT_QUANTITY_ROUNDING.get(symbol.upper(), 4)
    multiplier = 10 ** decimals
    return math.ceil(qty * multiplier) / multiplier
    
# Testattu ja toimii, kunhan vaan kaikki positiot on suljettu ja modea vaihtelee: 0 = one way mode & 3 = hedge
def set_hedge_mode(client, symbol: str, category: str = "linear", coin: str = "USDT"):

    try:
        response_pos = client.get_positions(category=category, symbol=symbol)
        positions = response_pos["result"]["list"]
        mode_values = {int(pos.get("positionIdx",0)) for pos in positions if pos["symbol"] == symbol}
        current_idx = mode_values.pop() if mode_values else 0
        if current_idx in (1,2):
            # print(f"✅ Hedge-tila on jo asetettu. Ei muutoksia. {current_idx}")
            return
        else:
            # Tarkista avoimet positiot
            response_pos = client.get_positions(category=category, symbol=symbol)
            open_positions = response_pos.get("result", {}).get("list", [])
            if any(float(pos.get("size", 0)) > 0 for pos in open_positions):
                print(f"⚠️ Ei voida vaihtaa hedge-modea: Avoimia positioita on olemassa symbolilla {symbol}.")
                return

            # Tarkista avoimet toimeksiannot
            response_orders = client.get_open_orders(category=category, symbol=symbol)
            open_orders = response_orders.get("result", {}).get("list", [])
            if open_orders:
                print(f"⚠️ Ei voida vaihtaa hedge-modea: Avoimia toimeksiantoja on olemassa symbolilla {symbol}.")
                return

        # Vaihdetaan hedge-tilaan coin-tasolla
        response = client.switch_position_mode(
            category=category,
            coin=coin.upper(),
            mode=3  # Single way mode = 0, Hedge-mode = 3
        )
        print(f"✅ Hedge-tila asetettu coin-tasolla ({coin.upper()}): {response}")

    except Exception as e:
        print(f"❌ Hedge-mode -asetuksen virhe: {e}")


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

from scripts.trade_order_logger import load_trade_logs, update_order_status


def set_stop_loss_and_trailing_stop(symbol, side, partial_stop_loss_price, trailing_stop_callback):
    position_idx = 1 if side == "Buy" else 2
    return client.set_trading_stop(
        category="linear",
        symbol=symbol,
        stopLoss=str(partial_stop_loss_price),
        trailingStop=str(trailing_stop_callback),
        slTriggerBy="LastPrice",
        tpslMode="Partial",
        positionIdx=position_idx
    )

def parse_percent(value_str):
    """Muuntaa '0.15%' → 0.0015 desimaalimuotoon"""
    return float(value_str.strip('%')) / 100

def has_open_limit_order(symbol, side, category="linear"):
    try:
        response = client.get_open_orders(category=category, symbol=symbol)
        open_orders = response["result"]["list"]

        for order in open_orders:
            if order["orderType"].lower() == "limit" and order["side"].lower() == side.lower():
                return True
        return False
    except Exception as e:
        print(f"❌ Failed to check open orders for {symbol} ({side}): {e}")
        return False
