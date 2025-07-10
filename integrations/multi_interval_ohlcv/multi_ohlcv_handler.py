# integrations/multi_interval_ohlcv/multi_ohlcv_handler.py

from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands
from shutil import copyfile

import os
import sys
import time
import json
import logging
import numpy as np 
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from configs.config import MULTI_INTERVAL_EXCHANGE_PRIORITY, DEFAULT_OHLCV_LIMIT, DEFAULT_INTERVALS, LOCAL_TIMEZONE
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

def truncate_log_if_too_large(log_path: Path = LOG_FILE_PATH):
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
    last_rsi = rsi.iloc[-1] if not rsi.empty else None
    result["rsi"] = round(last_rsi, 2) if last_rsi is not None and not np.isnan(last_rsi) else None

    # EMA
    ema = EMAIndicator(close=close, window=20).ema_indicator()
    last_ema = ema.iloc[-1] if not ema.empty else None
    result["ema"] = round(last_ema, 2) if last_ema is not None and not np.isnan(last_ema) else None

    # MACD
    macd_obj = MACD(close=close)
    macd_val = macd_obj.macd().iloc[-1] if not macd_obj.macd().empty else None
    signal_val = macd_obj.macd_signal().iloc[-1] if not macd_obj.macd_signal().empty else None
    result["macd"] = round(macd_val, 2) if macd_val is not None and not np.isnan(macd_val) else None
    result["macd_signal"] = round(signal_val, 2) if signal_val is not None and not np.isnan(signal_val) else None

    # Bollinger Bands
    bb = BollingerBands(close=close, window=20)
    upper = bb.bollinger_hband().iloc[-1] if not bb.bollinger_hband().empty else None
    lower = bb.bollinger_lband().iloc[-1] if not bb.bollinger_lband().empty else None
    result["bb_upper"] = round(upper, 2) if upper is not None and not np.isnan(upper) else None
    result["bb_lower"] = round(lower, 2) if lower is not None and not np.isnan(lower) else None

    return result

def save_fetch_log_with_data(symbol, intervals, limit, start_time, end_time, source_exchange, data_by_interval, log_path: Path = LOG_FILE_PATH):
    truncate_log_if_too_large(log_path)

    log_entry = {
        "timestamp": datetime.now(LOCAL_TIMEZONE).isoformat(),
        "source_exchange": source_exchange,
        "symbol": symbol,
        "intervals": intervals,
        "data_preview": {},
        "limit": limit,
        "start_time": start_time,
        "end_time": end_time
    }

    for interval, df in data_by_interval.items():
        if df.empty:
            print(f"⚠️ Interval {interval} has empty DataFrame for {symbol}")
            continue
        if 'close' not in df.columns or df['close'].isnull().all():
            print(f"⚠️ Interval {interval} missing valid close prices for {symbol}")
            continue

        analysis = analyze_ohlcv(df)

        try:
            last_close = float(df["close"].iloc[-1])
            analysis["close"] = round(last_close, 4)
        except Exception:
            analysis["close"] = None

        log_entry["data_preview"][interval] = analysis

    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def fetch_ohlcv_fallback(symbol, intervals=None, limit=None, start_time=None, end_time=None, log_path: Path = LOG_FILE_PATH):
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
                save_fetch_log_with_data(
                    symbol, intervals, limit, start_time, end_time,
                    source_exchange, data_by_interval, log_path=log_path
                )
                return data_by_interval, source_exchange
            else:
                errors[exchange] = "Empty DataFrames"

        except Exception as e:
            errors[exchange] = str(e)
            logging.warning(f"⚠️ Error fetching {symbol} ({exchange}): {e}")

    logging.error(f"❌ Failed to fetch OHLCV data from all exchanges. Errors: {errors}")
    print(f"\033[93m⚠️ This coin pair can't be found from any supported exchange: {symbol}\033[0m")
    return None, None

def test_single_exchange_ohlcv(symbol, exchange_name, intervals=None):
    print(f"\n🔍 Testing OHLCV fetch from: {exchange_name} for symbol {symbol}")
    fetch_fn = FETCH_FUNCTIONS.get(exchange_name)
    if not fetch_fn:
        print(f"❌ Fetch function for {exchange_name} not found.")
        return

    try:
        data_by_interval, source = fetch_fn(symbol, intervals=intervals)
        if not any(not df.empty for df in data_by_interval.values()):
            print(f"⚠️  No data fetched from {exchange_name} for {symbol}")
        else:
            print(f"✅ Successfully fetched OHLCV from {source}")
            for interval, df in data_by_interval.items():
                if df.empty:
                    print(f"  - {interval}: ❌ empty")
                else:
                    print(f"  - {interval}: ✅ {len(df)} rows")
    except Exception as e:
        print(f"❌ Exception while fetching from {exchange_name}: {e}")

if __name__ == "__main__":

    test_symbol = "BTCUSDT"
    test_intervals = ["1m", "5m", "1h"]  # voit säätää haluamasi

    test_single_exchange_ohlcv(test_symbol, "okx", intervals=test_intervals)
    test_single_exchange_ohlcv(test_symbol, "kucoin", intervals=test_intervals)
    test_single_exchange_ohlcv(test_symbol, "binance", intervals=test_intervals)
    test_single_exchange_ohlcv(test_symbol, "bybit", intervals=test_intervals)
