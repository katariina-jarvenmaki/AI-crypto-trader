# integrations/price_data_fetcher/utils.py
# version 2.0, aug 2025

from integrations.price_data_fetcher.fetchers.PriceDataFetcher import PriceDataFetcher
from modules.load_and_validate.load_and_validate import load_and_validate
from modules.pathbuilder.pathbuilder import pathbuilder

def config_and_log_loader():

    general_config = load_and_validate()
    symbol_paths = pathbuilder(extension=".jsonl", file_name=general_config["module_filenames"]["symbol_data_fetcher"], mid_folder="analysis")
    symbol_config = load_and_validate(file_path=symbol_paths["full_config_path"], schema_path=symbol_paths["full_config_schema_path"])
    symbol_log_path = symbol_paths["full_log_path"]
    module_paths = pathbuilder(
        extension=".jsonl", 
        file_name=general_config["module_filenames"]["price_data_fetcher"], 
        mid_folder="fetch"
    )
    module_log_path = module_paths["full_log_path"]
    module_log_schema_path = module_paths["full_log_schema_path"]
    module_config = load_and_validate(
        file_path=module_paths["full_config_path"],
        schema_path=module_paths["full_config_schema_path"]
    )

    return module_log_path, module_log_schema_path, module_config, symbol_config, symbol_log_path

def test_single_exchange(symbol, exchange_name):
    fetcher = PriceDataFetcher(symbol=symbol, order=[exchange_name])
    data = fetcher.fetch()
    print(f"[TEST] Data from {exchange_name}:", data)