# configs/config.py

# PLATFORMS
SUPPORTED_PLATFORMS = [
    "Binance",
]
DEFAULT_PLATFORM = "Binance"

# RSI_THRESHOLDS
RSI_THRESHOLDS = {
    "1w": {"buy": 35, "sell": 70, "buy_limit": None, "sell_limit": None},  # ylimmältä tasolta ei rajoja
    "1d": {"buy": 30, "sell": 70, "buy_limit": 70, "sell_limit": 55},      # limit-arvot määrittävät paljonko ylempi taso rajoittaa tätä tasoa
    "4h": {"buy": 30, "sell": 70, "buy_limit": 65, "sell_limit": 40},
    "2h": {"buy": 30, "sell": 70, "buy_limit": 60, "sell_limit": 40},
    "1h": {"buy": 30, "sell": 70, "buy_limit": 55, "sell_limit": 40},
    "30m":{"buy": 30, "sell": 70, "buy_limit": 55, "sell_limit": 45},
    "15m":{"buy": 28, "sell": 70, "buy_limit": 45, "sell_limit": 45},
    "5m": {"buy": 28, "sell": 70, "buy_limit": 45, "sell_limit": 55},
    "3m": {"buy": 28, "sell": 70, "buy_limit": 45, "sell_limit": 60},
    "1m": {"buy": 28, "sell": 72, "buy_limit": 35, "sell_limit": 65}
}

