import sys
import logging
import importlib
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# CONFIG INIT
from modules.pathbuilder.pathbuilder import pathbuilder
from utils.config_reader import config_reader

general_config = config_reader()
paths = pathbuilder(extension=".json", file_name=general_config["module_filenames"]["multi_interval_ohlcv"], mid_folder="fetch")
config = config_reader(config_path = paths["full_config_path"], schema_path = paths["full_schema_path"])

def fetch_ohlcv_fallback(symbol, intervals=None, limit=None, start_time=None, end_time=None):
    log_path = paths["full_log_path"]
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
                try:
                    # Tallennuslogiikka
                    print("Add saving here")
                    print("data:", data_by_interval)
                    print("source:", source_exchange)
                except Exception as log_err:
                    logging.warning(f"📝 Failed to save fetch log: {log_err}")

                return data_by_interval, source_exchange
            else:
                errors[exchange] = "Empty DataFrames"

        except Exception as e:
            errors[exchange] = str(e)
            logging.warning(f"⚠️ Error fetching {symbol} ({exchange}): {e}")

    logging.error(f"❌ Failed to fetch OHLCV data from all exchanges. Errors: {errors}")
    print(f"\033[93m⚠️ This coin pair can't be found from any supported exchange: {symbol}\033[0m")
    return None, None

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

    # Esimerkkitapa kutsua funktiota:
    symbol = "BTCUSDT"
    intervals = ["1h", "4h"]
    limit = 500

    data, source = fetch_ohlcv_fallback(symbol=symbol, intervals=intervals, limit=500)
    print(f"data: {data}")
    print(f"source: {source}")

    # test_symbol = "BTCUSDT"
    # test_intervals = ["1m", "5m", "1h"]
    # for exchange in config["exchange_priority"]:
    #     test_single_exchange_ohlcv(test_symbol, exchange, config, intervals=test_intervals)

if __name__ == "__main__":
    run_multi_exchange_ohlcv_test()
