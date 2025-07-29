import sys
import importlib
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# CONFIG INIT
from utils.config_reader import config_reader

config = config_reader(extension=".json", file_name="multi_ohlcv_fetch", mid_folder="fetch")

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
    test_symbol = "BTCUSDT"
    test_intervals = ["1m", "5m", "1h"]
    for exchange in config["exchange_priority"]:
        test_single_exchange_ohlcv(test_symbol, exchange, config, intervals=test_intervals)

if __name__ == "__main__":
    run_multi_exchange_ohlcv_test()
