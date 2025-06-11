# market/market_analyzer.py
#
# Uses EMA20, EMA50, RSI, ADX and Volume_MA20 to analyze
# General direction of the current market. Returns
# a market state and it's start time
#
import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator

class MarketAnalyzer:

    def __init__(self, df: pd.DataFrame, timeframe: str = "1d", use_volume_filter: bool = True):
        """
        df: DataFrame, jossa on sarakkeet ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        """
        self.df = df.copy()
        if 'timestamp' in self.df.columns:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df.set_index('timestamp', inplace=True)
        self.timeframe = timeframe
        self.use_volume_filter = use_volume_filter
        self._calculate_indicators()

    # Indicator calculation
    def _calculate_indicators(self):
        self.df['EMA20'] = EMAIndicator(close=self.df['close'], window=20).ema_indicator()
        self.df['EMA50'] = EMAIndicator(close=self.df['close'], window=50).ema_indicator()
        self.df['RSI'] = RSIIndicator(close=self.df['close'], window=14).rsi()
        adx = ADXIndicator(high=self.df['high'], low=self.df['low'], close=self.df['close'], window=14)
        self.df['ADX'] = adx.adx()
        self.df['Volume_MA20'] = self.df['volume'].rolling(window=20).mean()

    # Check if bull market
    def is_bull_market(self, i: int = -1) -> bool:
        row = self.df.iloc[i]
        return (
            row['EMA20'] > row['EMA50'] and
            row['ADX'] > 20 and
            row['RSI'] > 55 and
            (not self.use_volume_filter or row['volume'] > row['Volume_MA20'])
        )

    # Check if bear market
    def is_bear_market(self, i: int = -1) -> bool:
        row = self.df.iloc[i]
        return (
            row['EMA20'] < row['EMA50'] and
            row['ADX'] > 20 and
            row['RSI'] < 45 and
            (not self.use_volume_filter or row['volume'] > row['Volume_MA20'])
        )

    # Check if sideways market
    def is_sideways_market(self, i: int = -1) -> bool:
        row = self.df.iloc[i]
        ema_diff_ratio = abs(row['EMA20'] - row['EMA50']) / row['EMA50']
        return (
            ema_diff_ratio < 0.02 and
            row['ADX'] < 30 and
            35 < row['RSI'] < 65
        )

    # Check if volatile market without clear direction
    def is_volatile_market(self, i: int = -1, window_size: int = 20) -> bool:
        if i < window_size - 1:
            return False
        window = self.df.iloc[i - window_size + 1:i + 1]
        price_range = window['close'].max() - window['close'].min()
        mean_price = window['close'].mean()
        row = self.df.iloc[i]
        return (price_range / mean_price) > 0.07 and row['ADX'] > 20

    # Check if bullish consolidation
    def is_bullish_consolidation(self, i: int = -1) -> bool:
        if i < 19:
            return False
        window = self.df.iloc[i - 19:i + 1]
        row = self.df.iloc[i]
        in_range = window['close'].max() - window['close'].min() < 0.05 * window['close'].mean()
        return (
            row['close'] > row['EMA20'] and
            row['EMA20'] > row['EMA50'] and
            row['ADX'] > 25 and
            in_range
        )

    # Check if bearish consolidation
    def is_bearish_consolidation(self, i: int = -1) -> bool:
        if i < 19:
            return False
        window = self.df.iloc[i - 19:i + 1]
        row = self.df.iloc[i]
        in_range = window['close'].max() - window['close'].min() < 0.05 * window['close'].mean()
        return (
            row['close'] < row['EMA20'] and
            row['EMA20'] < row['EMA50'] and
            row['ADX'] > 25 and
            in_range
        )

    # Define the market state
    def get_market_state(self, i: int = -1) -> str:
        if self.is_bull_market(i):
            return "bull"
        elif self.is_bear_market(i):
            return "bear"
        elif self.is_bullish_consolidation(i):
            return "bull_consolidation"
        elif self.is_bearish_consolidation(i):
            return "bear_consolidation"
        elif self.is_sideways_market(i):
            return "neutral_sideways"
        elif self.is_volatile_market(i):
            return "volatile"
        else:
            return "unknown"

    # Return the market state info
    def get_market_state_with_start_date(self) -> dict:
        """
        Palauttaa nykyisen markkinatilan sekä päivämäärän, jolloin kyseinen tila alkoi.
        """
        current_state = self.get_market_state()
        latest_index = self.df.index[-1]

        for i in range(len(self.df) - 2, -1, -1):
            past_state = self.get_market_state(i)
            if past_state != current_state:
                trend_start_date = self.df.index[i + 1]
                break
        else:
            trend_start_date = self.df.index[0]

        return {
            "state": current_state,
            "started_on": trend_start_date.isoformat(),
            "latest": latest_index.isoformat()
        }
