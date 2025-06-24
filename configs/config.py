# configs/config.py

from datetime import timedelta
import pytz

# TIMEZONE
TIMEZONE = pytz.timezone("Europe/Helsinki")

# PLATFORMS
SUPPORTED_PLATFORMS = [
    "Binance",
]
DEFAULT_PLATFORM = "Binance"

# OHLCV INTEGRATIONS (from least used to most to save requests)
MULTI_INTERVAL_EXCHANGE_PRIORITY = ["okx", "kucoin", "binance", "bybit"]
DEFAULT_INTERVALS = [
    "1m", "3m", "5m", "15m", "30m",
    "1h", "2h", "4h", "1d", "1w"
]
DEFAULT_OHLCV_LIMIT = 200

# DIVERGENCE SETTINGS
# scripts/divergence_detector.py

RSI_LENGTH = 14

# Sensitivity values
BEARISH_RSI_DIFF = 0.5
BEARISH_PRICE_FACTOR = 1.001

BULLISH_RSI_DIFF = 1.5
BULLISH_PRICE_FACTOR = 0.998

# Signal agelimit in minutes
RECENT_THRESHOLD_MINUTES = 30

# RSI ANALYZER SETTINGS
# scripts/rsi_analyzer.py

RSI_PERIOD = 14

# Default values, if others are not defined
DEFAULT_BUY_LIMIT = 100
DEFAULT_SELL_LIMIT = 0

# Thresholds
RSI_THRESHOLDS = {
    "1w": {"buy": 35, "sell": 70, "buy_limit": None, "sell_limit": None},  # No limits on highest level
    "1d": {"buy": 30, "sell": 70, "buy_limit": 70, "sell_limit": 55},      # Limit-values define how much higher level limits this one 
    "4h": {"buy": 30, "sell": 70, "buy_limit": 65, "sell_limit": 40},
    "2h": {"buy": 30, "sell": 70, "buy_limit": 60, "sell_limit": 40},
    "1h": {"buy": 30, "sell": 70, "buy_limit": 55, "sell_limit": 40},
    "30m":{"buy": 30, "sell": 70, "buy_limit": 55, "sell_limit": 45},
    "15m":{"buy": 28, "sell": 70, "buy_limit": 45, "sell_limit": 45},
    "5m": {"buy": 28, "sell": 70, "buy_limit": 45, "sell_limit": 55},
    "3m": {"buy": 28, "sell": 70, "buy_limit": 45, "sell_limit": 60},
    "1m": {"buy": 28, "sell": 72, "buy_limit": 35, "sell_limit": 65}
}

# SIGNAL LIMITER SETTINGS
# scripts/signal_limiter.py
LOG_FILE = "logs/signals_log.json"
SIGNAL_TIMEOUT = timedelta(hours=1)

# SIGNAL LOGGER SETTINGS
# scripts/signal_logger.py
SIGNAL_LOG_JSON = "signals_log.json"
SIGNAL_LOG_TEXT = "signals.log"

# LOG BASED SIGNAL
# signals/log_based_signal.py
LOG_BASED_SIGNAL_TIMEOUT = timedelta(hours=24)

# Rsi-filter settings
RSI_FILTER_ENABLED = True
RSI_FILTER_INTERVAL = '4h'
RSI_FILTER_PERIOD = 14
RSI_FILTER_BUY_MAX = 65     # BUY only if RSI < 48
RSI_FILTER_SELL_MIN = 40    # SELL only if RSI > 52

# MINIUM PRICE CALCULATION
# scripts/min_buy_calc.py

# MINIMUM TRADE VALUE (fallback)
DEFAULT_MIN_NOTIONAL = 5.0  

# BUY MULTIPLIER (can be adjusted by strategy)
BUY_PRICE_MULTIPLIER = 1  

TRADE_LOG_FILE = "logs/order_log.json"

PRICE_CHANGE_LIMITS = {
    "buy": {
        "24h": 6.0,
        "18h": 6.0,
        "12h": 4.0,
        "6h": 2.0,
        "4h": 1.0,
        "3h": 0.5,
        "2h": 0.2,
    },
    "sell": {
        "24h": -6.0,
        "18h": -6.0,
        "12h": -4.0,
        "6h": -2.0,
        "4h": -1.0,
        "3h": -0.5,
        "2h": -0.2,
    },
}

# Stop loss -prosentit
BUY_FIRST_STOP_LOSS_PERCENT = 0.0006  # 0.06% Minium with ETH
BUY_SET_STOP_LOSS_PERCENT = 0.0036   # 0.36% Minium with ETH
BUY_TRAILING_STOP_LOSS_PERCENT = 0.0036 # 0.36% Minium with ETH
BUY_CLOSE_ORDER_LIMIT = 1.015

SELL_FIRST_STOP_LOSS_PERCENT = 0.0006  # 0.06% Minium with ETH
SELL_SET_STOP_LOSS_PERCENT = 0.0036   # 0.36% Minium with ETH
SELL_TRAILING_STOP_LOSS_PERCENT = 0.0036 # 0.36% Minium with ETH
SELL_CLOSE_ORDER_LIMIT = 0.985

# Volume multipliers per symbol and signal
VOLUME_MULTIPLIERS = {
    'BTCUSDC': {'buy': 1.2, 'sell': 1.2},
    'ETHUSDC': {'buy': 1.2, 'sell': 1.2},
    'SOLUSDC': {'buy': 1.2, 'sell': 1.3},
    'XRPUSDC': {'buy': 1.2, 'sell': 1.4},
    'ADAUSDC': {'buy': 1.2, 'sell': 1.5},
    'HBARUSDC': {'buy': 1.2, 'sell': 1.5},
    # Default arvot
    'DEFAULT': {'buy': 1.5, 'sell': 1.5},
}
