# integrations/multi_interval_ohlcv/multi_ohlcv_handler.py

from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands
from shutil import copyfile

import os
import time
import json
import logging

from pathlib import Path
from datetime import datetime
from configs.config import MULTI_INTERVAL_EXCHANGE_PRIORITY, DEFAULT_OHLCV_LIMIT, DEFAULT_INTERVALS
from integrations.multi_interval_ohlcv.fetch_ohlcv_okx_for_intervals import fetch_ohlcv_okx
from integrations.multi_interval_ohlcv.fetch_ohlcv_kucoin_for_intervals import fetch_ohlcv_kucoin
from integrations.multi_interval_ohlcv.fetch_ohlcv_bybit_for_intervals import fetch_ohlcv_bybit
from integrations.multi_interval_ohlcv.fetch_ohlcv_binance_for_intervals import fetch_ohlcv_binance

FETCH_FUNCTIONS = {
    'okx': fetch_ohlcv_okx,
    'kucoin': fetch_ohlcv_kucoin,
    'binance': fetch_ohlcv_binance,
    'bybit': fetch_ohlcv_bybit
}

LOG_FILE_PATH = Path("integrations/multi_interval_ohlcv/ohlcv_fetch_log.jsonl")

# LOG CLEANUP
MAX_LOG_SIZE_MB = 10
ENTRIES_TO_KEEP = 2000  

def truncate_log_if_too_large(log_path: Path):
    if not log_path.exists():
        return

    size_mb = os.path.getsize(log_path) / (1024 * 1024)
    if size_mb < MAX_LOG_SIZE_MB:
        return

    with log_path.open("r") as f:
        lines = f.readlines()

    # Keep the last entries
    lines_to_keep = lines[-ENTRIES_TO_KEEP:]

    archive_name = log_path.with_name(f"{log_path.stem}_{int(time.time())}.backup.jsonl")
    copyfile(log_path, archive_name)

    with log_path.open("w") as f:
        f.writelines(lines_to_keep)

    logging.info(f"🧹 Log file {log_path.name} cleaned: kept the last {len(lines_to_keep)} lines.")

def analyze_ohlcv(df):
    if df.empty or 'close' not in df.columns:
        return {}

    result = {}
    close = df["close"]

    # RSI
    rsi = RSIIndicator(close=close, window=14).rsi()
    result["rsi"] = round(rsi.iloc[-1], 2) if not rsi.empty else None

    # EMA
    ema = EMAIndicator(close=close, window=20).ema_indicator()
    result["ema"] = round(ema.iloc[-1], 2) if not ema.empty else None

    # MACD
    macd = MACD(close=close)
    result["macd"] = round(macd.macd().iloc[-1], 2) if not macd.macd().empty else None
    result["macd_signal"] = round(macd.macd_signal().iloc[-1], 2) if not macd.macd_signal().empty else None

    # Bollinger Bands
    bb = BollingerBands(close=close, window=20)
    result["bb_upper"] = round(bb.bollinger_hband().iloc[-1], 2) if not bb.bollinger_hband().empty else None
    result["bb_lower"] = round(bb.bollinger_lband().iloc[-1], 2) if not bb.bollinger_lband().empty else None

    return result

def save_fetch_log_with_data(symbol, intervals, limit, start_time, end_time, source_exchange, data_by_interval):

    truncate_log_if_too_large(LOG_FILE_PATH)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "source_exchange": source_exchange,
        "symbol": symbol,
        "intervals": intervals,
        "data_preview": {},
        "limit": limit,
        "start_time": start_time,
        "end_time": end_time
    }

    for interval, df in data_by_interval.items():
        analysis = analyze_ohlcv(df)
        log_entry["data_preview"][interval] = analysis

    with open(LOG_FILE_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def fetch_ohlcv_fallback(symbol, intervals=None, limit=None, start_time=None, end_time=None):
    intervals = intervals or DEFAULT_INTERVALS
    limit = limit or DEFAULT_OHLCV_LIMIT
    errors = {}

    for exchange in MULTI_INTERVAL_EXCHANGE_PRIORITY:
        fetch_fn = FETCH_FUNCTIONS.get(exchange)
        if not fetch_fn:
            logging.warning(f"[{exchange}] Fetch function not defined.")
            continue

        try:
            logging.info(f"🔍 Trying to fetch OHLCV data for {symbol} ({intervals}) from exchange {exchange}")
            data_by_interval, source_exchange = fetch_fn(
                symbol, intervals, limit=limit,
                start_time=start_time, end_time=end_time
            )

            if any(not df.empty for df in data_by_interval.values()):
                logging.info(f"✅ Fetch successful: {symbol} ({source_exchange})")
                save_fetch_log_with_data(symbol, intervals, limit, start_time, end_time, source_exchange, data_by_interval)
                return data_by_interval, source_exchange
            else:
                errors[exchange] = "Empty DataFrames"

        except Exception as e:
            errors[exchange] = str(e)
            logging.warning(f"⚠️ Error fetching {symbol} ({exchange}): {e}")

    logging.error(f"❌ Failed to fetch OHLCV data from all exchanges. Errors: {errors}")
    print(f"\033[93m⚠️ This coin pair can't be found from any supported exchange: {symbol}\033[0m")
    return None, None
