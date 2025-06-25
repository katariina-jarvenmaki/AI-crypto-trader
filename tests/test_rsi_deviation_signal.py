# tests/test_rsi_deviation_signal.py
# this is a test for log_momentum_signal.py limits
import pandas as pd
from binance.client import Client
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import matplotlib.pyplot as plt
import os
import sys

# Lisää polkuja jos tarvitset omia moduleja
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Aseta API-avaimet
from configs.credentials import BINANCE_API_KEY, BINANCE_API_SECRET

client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)

def fetch_1h_ohlcv(symbol: str, limit=500):
    klines = client.get_klines(symbol=symbol, interval="1h", limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
    ])
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df.astype(float)
    return df

def analyze_rsi_deviation(df, rsi_period=14, sma_period=20, rsi_overbought=70, rsi_oversold=30, dev_threshold=0.01):
    close = df["close"]
    rsi = RSIIndicator(close, window=rsi_period).rsi()
    sma = SMAIndicator(close, window=sma_period).sma_indicator()
    deviation = (close - sma) / sma

    df["RSI"] = rsi
    df["SMA"] = sma
    df["Deviation"] = deviation

    df["Signal"] = None
    df.loc[(rsi > rsi_overbought) & (deviation > dev_threshold), "Signal"] = "sell"
    df.loc[(rsi < rsi_oversold) & (deviation < -dev_threshold), "Signal"] = "buy"
    return df

def main():
    symbol = "BTCUSDT"
    df = fetch_1h_ohlcv(symbol)

    result = analyze_rsi_deviation(df)

    print("📊 Signaaleja havaittu:")
    print(result[result["Signal"].notnull()][["close", "RSI", "Deviation", "Signal"]])

    # Valinnainen: visualisoi
    plt.figure(figsize=(14, 6))
    plt.plot(result.index, result["close"], label="Close")
    plt.plot(result.index, result["SMA"], label="SMA20", linestyle="--")
    buy_signals = result[result["Signal"] == "buy"]
    sell_signals = result[result["Signal"] == "sell"]
    plt.scatter(buy_signals.index, buy_signals["close"], color="green", label="Buy Signal", marker="^", s=100)
    plt.scatter(sell_signals.index, sell_signals["close"], color="red", label="Sell Signal", marker="v", s=100)
    plt.legend()
    plt.title(f"{symbol} RSI + SMA deviation signals (1h)")
    plt.grid(True)
    plt.tight_layout()

    # Tuottojen laskenta signaalien perusteella
    signals = result[result["Signal"].notnull()][["close", "Signal"]].copy()
    signals["Trade"] = None
    signals["Trade PNL"] = None

    position = None  # {'side': 'long'/'short', 'price': float, 'timestamp': Timestamp}
    for timestamp, row in signals.iterrows():
        signal = row["Signal"]
        price = row["close"]

        if position is None:
            # Avaa positio
            position = {
                "side": "long" if signal == "buy" else "short",
                "price": price,
                "timestamp": timestamp
            }
            signals.at[timestamp, "Trade"] = "entry"
        else:
            # Sulje positio
            entry_price = position["price"]
            side = position["side"]
            if (side == "long" and signal == "sell") or (side == "short" and signal == "buy"):
                # Laske tuotto
                if side == "long":
                    pnl = (price - entry_price) / entry_price
                else:
                    pnl = (entry_price - price) / entry_price

                signals.at[timestamp, "Trade"] = "exit"
                signals.at[timestamp, "Trade PNL"] = round(pnl * 100, 2)
                position = None
            else:
                # Signaali ei sulje positiota → jätä väliin
                continue

    print("\n📈 Toteutuneet signaalit ja tuotot (long + short):")
    print(signals.dropna(subset=["Trade"]))

    total_pnl = signals["Trade PNL"].dropna().sum()
    trade_count = signals["Trade PNL"].dropna().count()
    print(f"\n💰 Yhteensä toteutuneita kauppoja: {trade_count}")
    print(f"📊 Kokonaistuotto: {total_pnl:.2f}%")


    plt.show()

if __name__ == "__main__":
    main()
