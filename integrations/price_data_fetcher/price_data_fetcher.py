# integrations/price_data_fetcher/price_data_fetcher.py

from modules.pathbuilder.pathbuilder import pathbuilder
from integrations.price_data_fetcher.utils import test_single_exchange
from modules.load_and_validate.load_and_validate import load_and_validate

def config_and_log_definer():

    general_config = load_and_validate()
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

    return module_log_path, module_log_schema_path, module_config

def price_data_fetcher():

    print("Running a Price Data Fetcher...")

    module_log_path, module_log_schema_path, module_config = config_and_log_definer()
    print(f"module_log_path: {module_log_path}")
    print(f"module_log_schema_path: {module_log_schema_path}")
    print(f"module_config: {module_config}")

if __name__ == "__main__":

    price_data_fetcher()
    # test_single_exchange("BTCUSDT", "okx")
    # test_single_exchange("BTCUSDT", "kucoin")
    # test_single_exchange("BTCUSDT", "binance")
    # test_single_exchange("BTCUSDT", "bybit")