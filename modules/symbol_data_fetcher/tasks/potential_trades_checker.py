
from pathlib import Path
from utils.get_timestamp import get_timestamp 
from modules.pathbuilder.pathbuilder import pathbuilder
from modules.load_and_validate.load_and_validate import load_and_validate 

def get_symbols_to_scan():
    return [
        s for s in module_config["supported_symbols"]
        if s not in module_config["main_symbols"] and s not in module_config["blocked_symbols"]
    ]

def run_potential_trades_checker(general_config, module_config, ohlcv_log_path):

    symbols_to_process = get_symbols_to_scan()
    paths = pathbuilder(extension=".jsonl", file_name=general_config["module_filenames"]["potential_trades_checker"], mid_folder="analysis")
    temporary_path = paths["full_temp_log_path"]
    schema_path = paths["full_log_schema_path"]
    timestamp = get_timestamp()

    print(f"🔍 Scanning {len(symbols_to_process)} symbols at {timestamp}")

    for symbol in symbols_to_process:
        print(f"\n🔁 Checking symbol: {symbol}")

        # print(f"temporary_path: {temporary_path}")
        # print(f"schema_path: {schema_path}")

        # print(f"general_config: {general_config}")
        # print(f"module_config: {module_config}")

if __name__ == "__main__":

    general_config = load_and_validate()
    paths = pathbuilder(extension=".json", file_name=general_config["module_filenames"]["symbol_data_fetcher"], mid_folder="analysis")

    module_config = load_and_validate(file_path=paths["full_config_path"], schema_path=paths["full_config_schema_path"])

    log_paths = pathbuilder(extension=".jsonl", file_name=general_config["module_filenames"]["multi_interval_ohlcv"], mid_folder="fetch")
    ohlcv_log_path = Path(log_paths["full_log_path"])
    print(f"ohlcv_log_path: {ohlcv_log_path}")
    run_potential_trades_checker(general_config, module_config, ohlcv_log_path)
