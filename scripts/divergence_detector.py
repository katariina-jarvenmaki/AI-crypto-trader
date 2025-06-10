# scripts/divergence_detector.py
import os
import pandas as pd
import pandas_ta as ta
from scipy.signal import find_peaks
from datetime import datetime, timedelta
from scripts.signal_logger import log_signal
from scripts.signal_limiter import is_signal_allowed, update_signal_log
from configs.config import (
    RSI_LENGTH,
    BEARISH_RSI_DIFF,
    BEARISH_PRICE_FACTOR,
    BULLISH_RSI_DIFF,
    BULLISH_PRICE_FACTOR,
    RECENT_THRESHOLD_MINUTES,
)

class DivergenceDetector:
    def __init__(self, df: pd.DataFrame, rsi_length: int = RSI_LENGTH):
        self.df = df.copy()

        if self.df.index.name == 'timestamp':
            self.df = self.df.reset_index()

        if 'timestamp' not in self.df.columns:
            raise ValueError("DataFrame must contain a 'timestamp' column.")

        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], utc=True)
        self.df.set_index('timestamp', inplace=True)
        self.df['rsi'] = ta.rsi(self.df['close'], length=rsi_length)
        self.now = pd.Timestamp.utcnow().tz_convert("UTC")

    def _find_peaks_and_troughs(self):
        peaks, _ = find_peaks(self.df['rsi'])
        troughs, _ = find_peaks(-self.df['rsi'])
        return peaks, troughs

    def _is_recent(self, timestamp, minutes=RECENT_THRESHOLD_MINUTES):
        return self.now - timestamp <= timedelta(minutes=minutes)

    def detect_bearish_divergence(self, symbol="UNKNOWN", interval="1h"):
        peaks, _ = self._find_peaks_and_troughs()
        signals = []
        for i in range(1, len(peaks)):
            curr, prev = peaks[i], peaks[i-1]
            time = self.df.index[curr]
            if not self._is_recent(time):
                continue
            if self.df['rsi'].iloc[curr] < self.df['rsi'].iloc[prev] - BEARISH_RSI_DIFF and \
               self.df['close'].iloc[curr] > self.df['close'].iloc[prev] * BEARISH_PRICE_FACTOR:
                if is_signal_allowed(symbol, interval, "sell", time, strategy="divergence"):
                    update_signal_log(symbol, interval, "sell", time, strategy="divergence")
                    log_signal("sell", f"divergence/{symbol}")
                    signals.append({
                        'type': 'bear',
                        'index': curr,
                        'price': self.df['close'].iloc[curr],
                        'time': time
                    })
        return signals[-1] if signals else None

    def detect_bullish_divergence(self, symbol="UNKNOWN", interval="1h"):
        _, troughs = self._find_peaks_and_troughs()
        signals = []
        for i in range(1, len(troughs)):
            curr, prev = troughs[i], troughs[i-1]
            time = self.df.index[curr]
            if not self._is_recent(time):
                continue
            if self.df['rsi'].iloc[curr] > self.df['rsi'].iloc[prev] + BULLISH_RSI_DIFF and \
               self.df['close'].iloc[curr] < self.df['close'].iloc[prev] * BULLISH_PRICE_FACTOR:
                if is_signal_allowed(symbol, interval, "buy", time, strategy="divergence"):
                    update_signal_log(symbol, interval, "buy", time, strategy="divergence")
                    log_signal("buy", f"divergence/{symbol}")
                    signals.append({
                        'type': 'bull',
                        'index': curr,
                        'price': self.df['close'].iloc[curr],
                        'time': time
                    })
        return signals[-1] if signals else None

    def detect_all_divergences(self, symbol="UNKNOWN", interval="1h"):
        bear = self.detect_bearish_divergence(symbol, interval)
        bull = self.detect_bullish_divergence(symbol, interval)
        signals = [s for s in [bear, bull] if s is not None]
        if signals:
            latest_signal = max(signals, key=lambda x: x['index'])
            latest_signal['strategy'] = 'divergence'
            return latest_signal
        return None