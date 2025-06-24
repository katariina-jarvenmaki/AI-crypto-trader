# tests/backtest_momentum_strategy.py
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from riskmanagement.momentum_validator import verify_signal_with_momentum_and_volume
from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback


def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Luo osto-/myyntisignaaleja yksinkertaisen momentumin perusteella."""
    df['price_change'] = df['close'].diff()
    df['signal'] = None

    for i in range(4, len(df)):
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
    volume_multiplier_used = None

    for i in range(interval * 2, len(df)):  # leave enough lookback for momentum
        row = df.iloc[:i]
        current = df.iloc[i]
        signal = current['signal']

        if signal in ['buy', 'sell']:
            result = verify_signal_with_momentum_and_volume(row, signal, symbol, intervals=[interval])

            strength = result.get('momentum_strength', '')
            volume_multiplier_used = result.get('volume_multiplier', None)

            if strength == 'strong':
                if position is None:
                    position = signal
                    entry_price = current['close']
                    trades.append({
                        'action': signal,
                        'entry_time': current.name,
                        'entry_price': entry_price,
                        'volume_multiplier': volume_multiplier_used
                    })
                elif position != signal:
                    # Close position
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
    # Käyttö: python backtest.py BTCUSDT 5m
    symbol = sys.argv[1] if len(sys.argv) > 1 else "HBARUSDT"
    interval = sys.argv[2] if len(sys.argv) > 2 else "5m"

    # Hae eiliseltä (klo 00:00–00:00)
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = today - timedelta(days=1)
    end_time = today

    candles, _ = fetch_ohlcv_fallback(symbol, [interval], limit=576, start_time=start_time, end_time=end_time)

    if interval in candles:
        df = candles[interval]
        trades = backtest(df, interval=5)
        for t in trades:
            print(t)
        calculate_summary(trades)
    else:
        print(f"❌ Failed to fetch data for {symbol} at interval {interval}")
