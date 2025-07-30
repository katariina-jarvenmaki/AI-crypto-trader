from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands
from shutil import copyfile

import sys
import json
import logging
import importlib
import numpy as np 
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# CONFIG INIT
from modules.pathbuilder.pathbuilder import pathbuilder
from modules.save_and_validate.save_and_validate import save_and_validate
from modules.load_and_validate.load_and_validate import load_and_validate
from utils.get_timestamp import get_timestamp 

general_config = load_and_validate()
paths = pathbuilder(extension=".jsonl", file_name=general_config["module_filenames"]["multi_interval_ohlcv"], mid_folder="fetch")
config = load_and_validate(file_path = paths["full_config_path"], schema_path = paths["full_config_schema_path"])

def fetch_ohlcv_fallback(symbol, intervals=None, limit=None, start_time=None, end_time=None, log_path = paths["full_log_path"]):

    intervals = intervals or config.get("intervals")
    limit = limit or config.get("ohlcv_limit")
    errors = {}

    exchange_priority = config.get("exchange_priority", [])
    fetch_functions = config.get("fetch_functions", {})

    for exchange in exchange_priority:
        fn_name = fetch_functions.get(exchange)
        if not fn_name:
            logging.warning(f"[{exchange}] Fetch function not defined.")
            continue

        try:
            logging.info(f"🔍 Trying to fetch OHLCV data for {symbol} ({intervals}) from exchange {exchange}")

            # Dynaaminen modulin ja funktion haku
            module_path = f"integrations.multi_interval_ohlcv.fetch_ohlcv_{exchange}_for_intervals"
            fetch_module = importlib.import_module(module_path)
            fetch_fn = getattr(fetch_module, fn_name)

            # Rakennetaan kutsuparametrit joustavasti
            fetch_kwargs = {
                "symbol": symbol,
                "intervals": intervals,
                "limit": limit
            }
            if start_time is not None and end_time is not None:
                fetch_kwargs["start_time"] = start_time
                fetch_kwargs["end_time"] = end_time

            # Suorita haku
            data_by_interval, source_exchange = fetch_fn(**fetch_kwargs)

            if any(not df.empty for df in data_by_interval.values()):
                logging.info(f"✅ Fetch successful: {symbol} ({source_exchange})")

                summarized_data = summarize_data_for_logging(data_by_interval)

                timestamp = get_timestamp()

                to_save = {
                    "timestamp": timestamp,
                    "source_exchange": source_exchange,
                    "symbol": symbol,
                    "intervals": intervals,
                    "data_preview": summarized_data,
                    "limit": limit,
                    "start_time": start_time,
                    "end_time": end_time,
                }

                save_and_validate(
                    data=to_save,
                    path=paths["full_log_path"],
                    schema=paths["full_log_schema_path"],
                    verbose=False
                )
                return to_save
                
            else:
                errors[exchange] = "Empty DataFrames"

        except Exception as e:
            errors[exchange] = str(e)
            logging.warning(f"⚠️ Error fetching {symbol} ({exchange}): {e}")

    logging.error(f"❌ Failed to fetch OHLCV data from all exchanges. Errors: {errors}")
    print(f"\033[93m⚠️ This coin pair can't be found from any supported exchange: {symbol}\033[0m")
    return None

def summarize_data_for_logging(data_by_interval: dict[str, pd.DataFrame]) -> dict[str, dict]:
    """
    Tiivistää OHLCV-dataa analyysia varten logimerkintään.
    Tarkistaa että vaaditut analyysiarvot ovat mukana.
    """
    equired_analysis_keys = set(config.get("required_analysis_keys", []))
    summary = {}

    for interval, df in data_by_interval.items():
        if df.empty:
            print(f"⚠️ Interval {interval} has empty DataFrame")
            continue
        if 'close' not in df.columns or df['close'].isnull().all():
            print(f"⚠️ Interval {interval} missing valid close prices")
            continue

        analysis = analyze_ohlcv(df)

        try:
            last_close = float(df["close"].iloc[-1])
            analysis["close"] = round(last_close, 4)
        except Exception:
            analysis["close"] = None

        missing_keys = equired_analysis_keys - analysis.keys()
        if missing_keys:
            print(f"⚠️ Interval {interval} missing keys from analysis: {missing_keys}")

        summary[interval] = analysis

    return summary

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

def test_single_exchange_ohlcv(symbol, exchange, config, intervals=None):
    print(f"\n🔍 Testing OHLCV fetch from: {exchange} for symbol {symbol}")

    # Hakee funktion nimen konfiguraatiosta
    fn_name = config["fetch_functions"].get(exchange)
    if not fn_name:
        print(f"❌ Fetch function for {exchange} not defined in config.")
        return

    try:
        # Rakennetaan moduulin nimi tiedostojen mukaan
        module_path = f"integrations.multi_interval_ohlcv.fetch_ohlcv_{exchange}_for_intervals"
        fetch_module = importlib.import_module(module_path)

        # Haetaan itse funktio moduulista
        fetch_fn = getattr(fetch_module, fn_name)

        # Suoritetaan haku
        data_by_interval, source = fetch_fn(symbol, intervals=intervals)

        # Tulostetaan tulokset
        if not any(not df.empty for df in data_by_interval.values()):
            print(f"⚠️  No data fetched from {exchange} for {symbol}")
        else:
            print(f"✅ Successfully fetched OHLCV from {source}")
            for interval, df in data_by_interval.items():
                if df.empty:
                    print(f"  - {interval}: ❌ empty")
                else:
                    print(f"  - {interval}: ✅ {len(df)} rows")

    except Exception as e:
        print(f"❌ Exception while fetching from {exchange}: {e}")

def run_multi_exchange_ohlcv_test():
    symbol = "BTCUSDT"
    intervals = ["1h", "4h"]
    limit = 500

    result = fetch_ohlcv_fallback(symbol=symbol, intervals=intervals, limit=limit)
    if(result):
        print(result)
        print(f"✅ Data successfully fetched and saved")

if __name__ == "__main__":
    run_multi_exchange_ohlcv_test()
