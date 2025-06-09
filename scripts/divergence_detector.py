# divergence_detector.py
import pandas as pd
import pandas_ta as ta
from scipy.signal import find_peaks
from datetime import datetime, timedelta

class DivergenceDetector:
    def __init__(self, df: pd.DataFrame, rsi_length: int = 14):
        self.df = df.copy()  # ✅ Aseta ensin self.df

        if self.df.index.name == 'timestamp':
            self.df = self.df.reset_index()  # Muunna indeksistä sarake

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

    def _is_recent(self, timestamp, minutes=30):
        return self.now - timestamp <= timedelta(minutes=minutes)

    def detect_bearish_divergence(self):
        peaks, _ = self._find_peaks_and_troughs()
        signals = []
        for i in range(1, len(peaks)):
            curr, prev = peaks[i], peaks[i-1]
            time = self.df.index[curr]
            if not self._is_recent(time):
                continue
            if self.df['rsi'].iloc[curr] < self.df['rsi'].iloc[prev] - 0.5 and \
               self.df['close'].iloc[curr] > self.df['close'].iloc[prev] * 1.001:
                signals.append({
                    'type': 'bear',
                    'index': curr,
                    'price': self.df['close'].iloc[curr],
                    'time': time
                })
        return signals[-1] if signals else None

    def detect_bullish_divergence(self):
        _, troughs = self._find_peaks_and_troughs()
        signals = []
        for i in range(1, len(troughs)):
            curr, prev = troughs[i], troughs[i-1]
            time = self.df.index[curr]
            if not self._is_recent(time):
                continue
            if self.df['rsi'].iloc[curr] > self.df['rsi'].iloc[prev] + 1.5 and \
               self.df['close'].iloc[curr] < self.df['close'].iloc[prev] * 0.998:
                signals.append({
                    'type': 'bull',
                    'index': curr,
                    'price': self.df['close'].iloc[curr],
                    'time': time
                })
        return signals[-1] if signals else None

    def detect_all_divergences(self):
        bear = self.detect_bearish_divergence()
        bull = self.detect_bullish_divergence()
        signals = [s for s in [bear, bull] if s is not None]
        if not signals:
            return None
        return max(signals, key=lambda x: x['index'])
