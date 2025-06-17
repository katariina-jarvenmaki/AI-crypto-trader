import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from riskmanagement.momentum_validator import verify_signal_with_momentum_and_volume
from integrations.binance_api_client import fetch_ohlcv_for_intervals


def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Luo osto-/myyntisignaaleja yksinkertaisen momentuman perusteella."""
    df['price_change'] = df['close'].diff()
    df['signal'] = None

    for i in range(2, len(df)):
        recent = df['price_change'].iloc[i-2:i].mean()
        prev = df['price_change'].iloc[i-4:i-2].mean()

        if recent > 0 and prev <= 0:
            df.at[df.index[i], 'signal'] = 'buy'
        elif recent < 0 and prev >= 0:
            df.at[df.index[i], 'signal'] = 'sell'
    
    return df

def backtest(df: pd.DataFrame, interval: int = 5):
    df = generate_signals(df)
    trades = []
    position = None
    entry_price = 0.0

    for i in range(interval * 2, len(df)):  # leave enough lookback for momentum
        row = df.iloc[:i]
        current = df.iloc[i]
        signal = current['signal']

        if signal in ['buy', 'sell']:
            momentum = verify_signal_with_momentum_and_volume(row, signal, intervals=[interval])
            strength = momentum['momentum_strength']

            if strength == 'strong':
                if position is None:
                    position = signal
                    entry_price = current['close']
                    trades.append({
                        'action': signal,
                        'entry_time': current.name,
                        'entry_price': entry_price,
                    })
                elif position != signal:
                    # Close current position
                    exit_price = current['close']
                    pnl = (exit_price - entry_price) if position == 'buy' else (entry_price - exit_price)
                    trades[-1].update({
                        'exit_time': current.name,
                        'exit_price': exit_price,
                        'pnl': pnl
                    })
                    position = None

    return trades

def calculate_summary(trades: list):
    closed_trades = [t for t in trades if 'exit_price' in t]
    total_pnl = sum(t['pnl'] for t in closed_trades)
    win_rate = sum(1 for t in closed_trades if t['pnl'] > 0) / len(closed_trades) if closed_trades else 0

    print(f"\n🔍 Backtest Summary:")
    print(f"Total Trades: {len(closed_trades)}")
    print(f"Total P&L: {total_pnl:.2f}")
    print(f"Win Rate: {win_rate:.2%}")

if __name__ == "__main__":
    symbol = "HBARUSDT"
    interval = "5m"  # Binance interval
    candles = fetch_ohlcv_for_intervals(symbol, [interval], limit=500)

    if interval in candles:
        df = candles[interval]
        trades = backtest(df, interval=5)
        for t in trades:
            print(t)
        calculate_summary(trades)
    else:
        print(f"❌ Failed to fetch data for {interval}")
