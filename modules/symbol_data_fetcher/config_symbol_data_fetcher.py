# modules/symbol_data_fetcher/config_symbol_data_fetcher.py

from pathlib import Path
from zoneinfo import ZoneInfo

# === TIME & TIME-RELATED SETTINGS ===

# Timezone to use (modifiable as needed)
LOCAL_TIMEZONE = ZoneInfo("Europe/Helsinki")

# Defines how old OHLCV data is accepted (in minutes)
OHLCV_MAX_AGE_MINUTES = 180

# Length of analysis history in log (in days)
ANALYSIS_LOG_LOOKBACK_DAYS = 2

# Minimum time between two analyses (in hours)
ANALYSIS_MIN_INTERVAL_HOURS = 3


# === INTERVALS & WEIGHTS ===

# OHLCV intervals used
INTERVALS = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "1d", "1w"]

# Weights in analysis for different timeframes
INTERVAL_WEIGHTS = {
    "1h": 1.0,
    "4h": 1.5,
    "1d": 2.0,
}


# === PARAMETERS RELATED TO SYMBOL FETCHING ===

# Number of symbols selected for long/short recommendations
TOP_N_LONG = 30
TOP_N_SHORT = 30

# If multiple symbols share the same value, allow additional ties
TOP_N_EXTRA_TIES = True

# OHLCV data fetch limit per symbol
OHLCV_FETCH_LIMIT = 200

# Number of retries for writing to the log file
MAX_APPEND_RETRIES = 10


# === LOG FILES ===

# Path to OHLCV fetch log
OHLCV_LOG_PATH = Path("../AI-crypto-trader-logs/fetched-data/ohlcv_fetch_log.jsonl")

# Path to symbol data log
SYMBOL_LOG_PATH = Path("../AI-crypto-trader-logs/analysis-data/symbol_data_log.jsonl")


# === TASK CONFIGURATIONS FOR SYMBOL FETCHING ===

TASK_CONFIG = {
    "main": {
        "symbol_keys": ["potential_both_ways"],
        "cooldown_minutes": 2,
        "retry_delay": 3.0,
        "temp_log": "temporary_log_main_symbols.jsonl"
    },
    "top": {
        "symbol_keys": ["potential_to_long", "potential_to_short"],
        "cooldown_minutes": 1,
        "retry_delay": 8.0,
        "temp_log": "temporary_log_top_symbols.jsonl"
    },
    "potential": {
        "symbol_keys": ["potential_both_ways", "potential_to_long", "potential_to_short"],
        "cooldown_minutes": 5,
        "retry_delay": 57.0,
        "temp_log": "temporary_log_potential_trades.jsonl"
    }
}

# === SYMBOL LISTS ===

# Main symbols (most important, continuously monitored)
MAIN_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "HYPEUSDT", "SUIUSDT", 
    "LINKUSDT", "XLMUSDT", "LTCUSDT", "HBARUSDT"
]

# All supported symbols (manually maintained)
SUPPORTED_SYMBOLS = [
    # Symbol list continues...
    "BTCUSDT", 
    "ETHUSDT", 
    "XRPUSDT", 
    "BCHUSDT", 
    "LTCUSDT", 
    "XTZUSDT", 
    "LINKUSDT", 
    "ADAUSDT", 
    "DOTUSDT", 
    "UNIUSDT", 
    "XEMUSDT", 
    "SUSHIUSDT", 
    "AAVEUSDT", 
    "DOGEUSDT", 
    "ETCUSDT", 
    "BNBUSDT", 
    "FILUSDT", 
    "SOLUSDT", 
    "XLMUSDT", 
    "TRXUSDT", 
    "VETUSDT", 
    "THETAUSDT", 
    "COMPUSDT", 
    "AXSUSDT", 
    "SANDUSDT", 
    "MANAUSDT", 
    "KSMUSDT", 
    "ATOMUSDT", 
    "AVAXUSDT", 
    "CHZUSDT", 
    "CRVUSDT", 
    "ENJUSDT", 
    "GRTUSDT", 
    "SHIB1000USDT"
    "YFIUSDT", 
    "BSVUSDT",
    "ICPUSDT", 
    "ALGOUSDT", 
    "DYDXUSDT", 
    "NEARUSDT", 
    "IOSTUSDT", 
    "DASHUSDT", 
    "GALAUSDT", 
    "CELRUSDT", 
    "HBARUSDT", 
    "ONEUSDT", 
    "C98USDT", 
    "AGLDUSDT", 
    "MKRUSDT", 
    "COTIUSDT", 
    "ALICEUSDT", 
    "EGLDUSDT", 
    "RUNEUSDT", 
    "ILVUSDT", 
    "FLOWUSDT", 
    "WOOUSDT", 
    "LRCUSDT", 
    "ENSUSDT", 
    "IOTXUSDT", 
    "CHRUSDT", 
    "BATUSDT", 
    "STORJUSDT", 
    "SNXUSDT", 
    "SLPUSDT", 
    "ANKRUSDT", 
    "LPTUSDT", 
    "QTUMUSDT", 
    "CROUSDT", 
    "SXPUSDT", 
    "YGGUSDT", 
    "ZECUSDT", 
    "IMXUSDT", 
    "SFPUSDT", 
    "AUDIOUSDT", 
    "ZENUSDT", 
    "SKLUSDT", 
    "CVCUSDT", 
    "RSRUSDT", 
    "STXUSDT", 
    "MASKUSDT", 
    "CTKUSDT", 
    "REQUSDT", 
    "1INCHUSDT", 
    "SPELLUSDT", 
    "ARUSDT", 
    "XMRUSDT", 
    "PEOPLEUSDT", 
    "IOTAUSDT", 
    "ICXUSDT", 
    "CELOUSDT", 
    "WAVESUSDT", 
    "RVNUSDT", 
    "KNCUSDT", 
    "KAVAUSDT", 
    "ROSEUSDT", 
    "JASMYUSDT", 
    "QNTUSDT", 
    "ZILUSDT", 
    "NEOUSDT", 
    "CKBUSDT", 
    "SUNUSDT", 
    "JSTUSDT", 
    "BANDUSDT", 
    "API3USDT", 
    "PAXGUSDT", 
    "KDAUSDT", 
    "APEUSDT", 
    "GMTUSDT", 
    "OGNUSDT", 
    "CTSIUSDT", 
    "ARPAUSDT", 
    "ALPHAUSDT", 
    "ZRXUSDT", 
    "GLMRUSDT", 
    "SCRTUSDT", 
    "BAKEUSDT", 
    "ASTRUSDT", 
    "FXSUSDT", 
    "MINAUSDT", 
    "BOBAUSDT", 
    "1000XECUSDT",
    "ACHUSDT", 
    "BALUSDT", 
    "MTLUSDT", 
    "CVXUSDT", 
    "XCNUSDT", 
    "FLMUSDT", 
    "CTCUSDT", 
    "LUNA2USDT", 
    "OPUSDT", 
    "ONTUSDT", 
    "TRBUSDT", 
    "BELUSDT", 
    "USDCUSDT", 
    "LDOUSDT", 
    "INJUSDT", 
    "STGUSDT", 
    "1000LUNCUSDT",
    "ETHWUSDT", 
    "GMXUSDT", 
    "APTUSDT", 
    "TWTUSDT", 
    "MAGICUSDT", 
    "1000BONKUSDT",
    "HIGHUSDT", 
    "COREUSDT",
    "BLURUSDT", 
    "CFXUSDT", 
    "1000FLOKIUSDT",
    "SSVUSDT", 
    "RPLUSDT", 
    "TUSDT", 
    "TRUUSDT", 
    "LQTYUSDT", 
    "HFTUSDT", 
    "RLCUSDT", 
    "ARBUSDT", 
    "IDUSDT", 
    "JOEUSDT", 
    "SUIUSDT", 
    "1000PEPEUSDT",
    "EDUUSDT", 
    "ORDIUSDT", 
    "10000LADYSUSDT",
    "PHBUSDT", 
    "RADUSDT", 
    "UMAUSDT", 
    "TONUSDT", 
    "MBOXUSDT", 
    "VRUSDT", 
    "MAVUSDT", 
    "MDTUSDT", 
    "XVGUSDT", 
    "PENDLEUSDT", 
    "WLDUSDT", 
    "ARKMUSDT", 
    "AUCTIONUSDT", 
    "FORTHUSDT", 
    "ARKUSDT", 
    "KASUSDT", 
    "BNTUSDT", 
    "GLMUSDT", 
    "CYBERUSDT", 
    "SEIUSDT", 
    "HIFIUSDT", 
    "OGUSDT", 
    "NMRUSDT", 
    "PROMUSDT", 
    "PERPUSDT", 
    "XVSUSDT", 
    "MNTUSDT", 
    "ORBSUSDT", 
    "WAXPUSDT", 
    "BIGTIMEUSDT", 
    "GASUSDT", 
    "POLYXUSDT", 
    "POWRUSDT", 
    "STEEMUSDT", 
    "TIAUSDT", 
    "SNTUSDT", 
    "MEMEUSDT", 
    "CAKEUSDT", 
    "TOKENUSDT", 
    "BEAMUSDT", 
    "10000SATSUSDT",
    "AERGOUSDT", 
    "AGIUSDT", 
    "PYTHUSDT", 
    "GODSUSDT", 
    "1000RATSUSDT",
    "MOVRUSDT", 
    "SUPERUSDT", 
    "USTCUSDT", 
    "RAREUSDT", 
    "ONGUSDT", 
    "AXLUSDT", 
    "JTOUSDT", 
    "ACEUSDT", 
    "METISUSDT", 
    "XAIUSDT", 
    "WIFUSDT", 
    "AIUSDT", 
    "MANTAUSDT", 
    "MYROUSDT", 
    "ONDOUSDT", 
    "ALTUSDT", 
    "TAOUSDT", 
    "10000WENUSDT",
    "JUPUSDT", 
    "ZETAUSDT", 
    "CETUSUSDT", 
    "DYMUSDT", 
    "MAVIAUSDT", 
    "VTHOUSDT", 
    "PIXELUSDT", 
    "STRKUSDT", 
    "MOBILEUSDT", 
    "1000TURBOUSDT",
    "PORTALUSDT", 
    "SCAUSDT", 
    "AEVOUSDT", 
    "VANRYUSDT", 
    "BOMEUSDT", 
    "OMUSDT", 
    "SLERFUSDT", 
    "ETHFIUSDT", 
    "ZKUSDT", 
    "POPCATUSDT", 
    "ORCAUSDT", 
    "DEGENUSDT", 
    "ENAUSDT", 
    "WUSDT", 
    "TNSRUSDT", 
    "SAGAUSDT", 
    "ZBCNUSDT", 
    "OMNIUSDT", 
    "MERLUSDT", 
    "MEWUSDT", 
    "MELANIAUSDT",
    "BRETTUSDT", 
    "SAFEUSDT", 
    "REZUSDT", 
    "BBUSDT", 
    "VELOUSDT", 
    "NOTUSDT", 
    "1000000MOGUSDT",
    "DRIFTUSDT", 
    "PHAUSDT", 
    "RAYDIUMUSDT",
    "GRIFFAINUSDT", 
    "DOGUSDT",
    "TRUMPUSDT", 
    "PONKEUSDT", 
    "TAIKOUSDT", 
    "1000000BABYDOGEUSDT", 
    "IOUSDT", 
    "ATHUSDT", 
    "LISTAUSDT", 
    "ZROUSDT", 
    "AEROUSDT", 
    "AKTUSDT", 
    "AIXBTUSDT", 
    "10000QUBICUSDT",
    "HIVEUSDT", 
    "BIOUSDT", 
    "MOCAUSDT", 
    "PRCLUSDT", 
    "ZEREBROUSDT", 
    "UXLINKUSDT", 
    "A8USDT", 
    "BANANAUSDT", 
    "ARCUSDT", 
    "AVAILUSDT", 
    "DEXEUSDT", 
    "GUSDT", 
    "RENDERUSDT", 
    "AI16ZUSDT", 
    "CGPTUSDT", 
    "SWARMSUSDT", 
    "EIGENUSDT", 
    "NEIROETHUSDT",
    "DOGSUSDT", 
    "SYNUSDT", 
    "SUNDOGUSDT", 
    "SLFUSDT", 
    "CHESSUSDT", 
    "POLUSDT", 
    "AVAAIUSDT", 
    "KMNOUSDT", 
    "PRIMEUSDT", 
    "FLUXUSDT", 
    "CATIUSDT", 
    "HMSTRUSDT", 
    "1000CATUSDT", 
    "REXUSDT",
    "ALEOUSDT",
    "1000NEIROCTOUSDT", 
    "FBUSDT", 
    "COOKIEUSDT", 
    "FIDAUSDT", 
    "MOODENGUSDT", 
    "ALCHUSDT", 
    "SOLVUSDT", 
    "GRASSUSDT", 
    "ACTUSDT", 
    "SCRUSDT", 
    "PUFFERUSDT", 
    "CARVUSDT", 
    "SPXUSDT", 
    "DEEPUSDT", 
    "GOATUSDT", 
    "ALUUSDT", 
    "LUMIAUSDT", 
    "1000XUSDT",
    "TAIUSDT", 
    "VIRTUALUSDT", 
    "KAIAUSDT", 
    "SWELLUSDT", 
    "PNUTUSDT", 
    "COWUSDT", 
    "HYPEUSDT", 
    "MAJORUSDT", 
    "FARTCOINUSDT", 
    "BANUSDT", 
    "USUALUSDT", 
    "FLOCKUSDT", 
    "SUSDT", 
    "MORPHOUSDT", 
    "OLUSDT", 
    "CHILLGUYUSDT", 
    "ZRCUSDT", 
    "MEUSDT", 
    "1000000CHEEMSUSDT", 
    "COOKUSDT", 
    "THEUSDT", 
    "PENGUUSDT", 
    "SOLOUSDT",
    "1000TOSHIUSDT", 
    "MOVEUSDT", 
    "XIONUSDT", 
    "ACXUSDT", 
    "GIGAUSDT", 
    "KOMAUSDT", 
    "VELODROMEUSDT", 
    "VANAUSDT", 
    "PLUMEUSDT", 
    "ANIMEUSDT", 
    "VINEUSDT", 
    "10000ELONUSDT", 
    "VVVUSDT", 
    "JELLYJELLYUSDT", 
    "BERAUSDT", 
    "IPUSDT", 
    "TSTBSCUSDT", 
    "XDCUSDT", 
    "SOLAYERUSDT", 
    "B3USDT", 
    "SHELLUSDT", 
    "KAITOUSDT", 
    "GPSUSDT", 
    "AVLUSDT", 
    "REDUSDT", 
    "XTERUSDT", 
    "NILUSDT", 
    "ROAMUSDT", 
    "SERAPHUSDT", 
    "BMTUSDT", 
    "FORMUSDT", 
    "MUBARAKUSDT", 
    "TUTUSDT", 
    "SIRENUSDT", 
    "PARTIUSDT", 
    "WALUSDT", 
    "BANANAS31USDT",
    "GUNUSDT", 
    "BABYUSDT", 
    "XAUTUSDT", 
    "MLNUSDT", 
    "INITUSDT", 
    "KERNELUSDT", 
    "WCTUSDT", 
    "BANKUSDT",
    "EPTUSDT", 
    "HYPERUSDT", 
    "OBTUSDT", 
    "SIGNUSDT", 
    "PUNDIXUSDT", 
    "SXTUSDT", 
    "OBOLUSDT", 
    "SKYAIUSDT", 
    "SYRUPUSDT", 
    "SOONUSDT", 
    "BUSDT",
    "HUMAUSDT", 
    "AUSDT", 
    "SOPHUSDT", 
    "LAUSDT", 
    "SQDUSDT", 
    "SPKUSDT", 
    "SAHARAUSDT"
]

BLOCKED_SYMBOLS =  [ 
    "SHIB1000USDT", # -> not supported by exchanges 3.7.2025 
    "BSVUSDT", # -> not supported by exchanges 3.7.2025 
    "1000XECUSDT", # -> not supported by exchanges 3.7.2025 
    "LUNA2USDT", # -> not supported by exchanges 3.7.2025  
    "1000LUNCUSDT", # -> not supported by exchanges 3.7.2025 
    "1000BONKUSDT", # -> not supported by exchanges 3.7.2025  
    "COREUSDT", # -> not supported by exchanges 3.7.2025  
    "1000FLOKIUSDT", # -> not supported by exchanges 3.7.2025  
    "1000PEPEUSDT", # -> not supported by exchanges 3.7.2025 
    "10000LADYSUSDT", # -> not supported by exchanges 3.7.2025 
    "10000SATSUSDT", # -> not supported by exchanges 3.7.2025 
    "1000RATSUSDT", # -> not supported by exchanges 3.7.2025 
    "10000WENUSDT", # -> not supported by exchanges 3.7.2025 
    "1000TURBOUSDT", # -> not supported by exchanges 3.7.2025  
    "1000000MOGUSDT", # -> not supported by exchanges 3.7.2025 
    "RAYDIUMUSDT", # -> not supported by exchanges 3.7.2025 
    "DOGUSDT", # -> not supported by exchanges 3.7.2025 
    "1000000BABYDOGEUSDT", # -> not supported by exchanges 3.7.2025  
    "10000QUBICUSDT", # -> not supported by exchanges 3.7.2025 
    "NEIROETHUSDT", # -> not supported by exchanges 3.7.2025 
    "REXUSDT", # -> not supported by exchanges 3.7.2025 
    "ALEOUSDT", # -> not supported by exchanges 3.7.2025 
    "1000NEIROCTOUSDT", # -> not supported by exchanges 3.7.2025 
    "1000XUSDT", # -> not supported by exchanges 3.7.2025 
    "1000000CHEEMSUSDT", # -> not supported by exchanges 3.7.2025 
    "1000TOSHIUSDT", # -> not supported by exchanges 3.7.2025 
    "10000ELONUSDT", # -> not supported by exchanges 3.7.2025 
    "BANANAS31USDT", # -> just too manipulated, with continious short liquidations
    "BANKUSDT", # -> not supported by exchanges 3.7.2025 
    "SKYAIUSDT", # -> not supported by exchanges 3.7.2025 
    "BUSDT", # -> not supported by exchanges 3.7.2025
    "ZBCNUSDT", # -> too high fees 
    "HYPERUSDT", # -> too fast to move
    "VANRYUSDT", # -> too volatile without momentum checks
    "ALPHAUSDT", # -> too volatile without momentum checks
    "VANRYUSDT", # -> too volatile without momentum checks
    "SLFUSDT", # -> too volatile without momentum checks
    "SOLOUSDT", # -> too volatile without momentum checks
    "PENGUUSDT", # -> too volatile without momentum checks
]