# integrations/price_data_fetcher/price_data_fetcher.py

from modules.pathbuilder.pathbuilder import pathbuilder
from integrations.price_data_fetcher.utils import test_single_exchange
from modules.load_and_validate.load_and_validate import load_and_validate

if __name__ == "__main__":

    general_config = load_and_validate()
    module_paths = pathbuilder(
        extension=".jsonl", 
        file_name=general_config["module_filenames"]["price_data_fetcher"], 
        mid_folder="fetch"
    )
    module_log_path = module_paths["full_log_path"]
    module_schema_path = module_paths["full_log_schema_path"]
    module_config = load_and_validate(
        file_path=module_paths["full_config_path"],
        schema_path=module_paths["full_config_schema_path"]
    )
    print(f"module_config: {module_config}")

    # print(f": {}")
    # main()
    test_single_exchange("BTCUSDT", "okx")
    # test_single_exchange("BTCUSDT", "kucoin")
    # test_single_exchange("BTCUSDT", "binance")
    # test_single_exchange("BTCUSDT", "bybit")