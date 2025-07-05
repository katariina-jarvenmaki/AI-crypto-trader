# modules/symbol_data_fetcher/utils.py

import math
import time
import json
from pathlib import Path
from datetime import datetime, timedelta

from integrations.multi_interval_ohlcv.multi_ohlcv_handler import fetch_ohlcv_fallback
from modules.symbol_data_fetcher.symbol_data_fetcher_config import (
    INTERVAL_WEIGHTS,
    OHLCV_MAX_AGE_MINUTES,
    OHLCV_FETCH_LIMIT,
    OHLCV_LOG_PATH,
    SYMBOL_LOG_PATH,
    LOCAL_TIMEZONE,
    MAX_APPEND_RETRIES,
    INTERVALS,
)

def last_fetch_time(symbol: str):
    if not OHLCV_LOG_PATH.exists():
        return None

    with open(OHLCV_LOG_PATH, "r") as f:
        for line in reversed(list(f)):
            try:
                entry = json.loads(line)
                if entry.get("symbol") == symbol:
                    ts_str = entry.get("timestamp")
                    if ts_str:
                        dt = datetime.fromisoformat(ts_str)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=LOCAL_TIMEZONE)
                        return dt.astimezone(LOCAL_TIMEZONE)
            except json.JSONDecodeError:
                continue
    return None

def score_asset(data_preview):
    score = 0
    weight_map = INTERVAL_WEIGHTS

    for interval in weight_map:
        d = data_preview.get(interval)
        if not d:
            continue

        rsi = d.get("rsi")
        macd = d.get("macd")
        macd_signal = d.get("macd_signal")

        if rsi is not None and not math.isnan(rsi):
            if rsi > 70:
                score -= 1 * weight_map[interval]
            elif rsi < 30:
                score += 1 * weight_map[interval]

        if (macd is not None and not math.isnan(macd)) and (macd_signal is not None and not math.isnan(macd_signal)):
            if macd > macd_signal:
                score += 0.5 * weight_map[interval]
            elif macd < macd_signal:
                score -= 0.5 * weight_map[interval]

    return score

def prepare_temporary_log(log_name: str = "temp_log.jsonl") -> Path:

    """Luo tai tyhjentää lokaalin log-tiedoston samassa kansiossa kuin tämä tiedosto."""

    current_dir = Path(__file__).parent
    log_file = current_dir / log_name

    log_file.write_text("")

    return log_file

def append_temp_to_ohlcv_log_until_success(temp_path: Path, target_path: Path, max_retries: int = 5, retry_delay: float = 1.0):

    if not temp_path.exists():
        print(f"Temp file {temp_path} does not exist, nothing to append.")
        return

    if temp_path.stat().st_size == 0:
        print(f"Temp file {temp_path} is empty, skipping append.")
        return

    for attempt in range(1, max_retries + 1):
        try:
            with open(temp_path, "r") as temp_file:
                temp_lines = temp_file.readlines()

            with open(target_path, "a") as target_file:
                target_file.writelines(temp_lines)

            with open(target_path, "r") as target_file:
                target_lines = target_file.readlines()

            if target_lines[-len(temp_lines):] == temp_lines:
                print(f"Successfully appended temp file contents to {target_path} on attempt {attempt}.")
                break
            else:
                raise IOError("Verification failed: appended lines not found in target file.")

        except Exception as e:
            print(f"Attempt {attempt} failed with error: {e}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached, failed to append temp file.")
                raise

def generic_load_symbols(SYMBOL_KEYS, SYMBOL_LOG_PATH):

    if not SYMBOL_LOG_PATH.exists():
        print(f"❌ File not found: {SYMBOL_LOG_PATH}")
        return []

    try:
        with open(SYMBOL_LOG_PATH, "r") as f:
            lines = f.readlines()
            if not lines:
                print("⚠️ File is empty.")
                return []

            data = json.loads(lines[-1].strip())
            symbols = set()
            for key in SYMBOL_KEYS:
                symbols.update(data.get(key, []))
            return list(symbols)

    except Exception as e:
        print(f"⚠️ Failed loading symbols: {e}")
        return []

def fetch_symbols_data(
    SYMBOL_KEYS,
    TEMP_SYMBOLS_LOG,
    SYMBOL_FETCH_COOLDOWN_MINUTES,
    APPEND_RETRY_DELAY_SECONDS
):
    """
    Yleinen symbolien OHLCV-datan hakufunktio.
    """
    symbols = generic_load_symbols(SYMBOL_KEYS, SYMBOL_LOG_PATH)
    if not symbols:
        print("⚠️ No symbols to fetch.")
        return

    print(f"🔄 Fetching OHLCV data for {len(symbols)} symbols...")

    temporary_path = prepare_temporary_log(TEMP_SYMBOLS_LOG)
 
    for symbol in symbols:
        try:
            last_fetched = last_fetch_time(symbol)
            if last_fetched:
                age = datetime.now(LOCAL_TIMEZONE) - last_fetched
                if age < timedelta(minutes=SYMBOL_FETCH_COOLDOWN_MINUTES):
                    print(f"⏩ Skipping {symbol}, fetched {age.total_seconds() // 60:.1f} min ago.")
                    continue
        except Exception as e:
            print(f"⚠️ Failed to check last fetch for {symbol}: {e}")

        print(f"📥 Fetching: {symbol}")

        try:
            result_data, status = fetch_ohlcv_fallback(
                symbol=symbol,
                intervals=INTERVALS,
                limit=OHLCV_FETCH_LIMIT,
                log_path=temporary_path
            )
            if not status:
                print(f"⚠️ Fetch failed for {symbol}.")
        except Exception as e:
            print(f"❌ Error while fetching data for {symbol}: {e}")

    try:
        append_temp_to_ohlcv_log_until_success(
            temp_path=temporary_path,
            target_path=OHLCV_LOG_PATH,
            max_retries=MAX_APPEND_RETRIES,
            retry_delay=APPEND_RETRY_DELAY_SECONDS
        )
    except Exception as e:
        print(f"❌ Failed to append temp log to OHLCV log: {e}")
