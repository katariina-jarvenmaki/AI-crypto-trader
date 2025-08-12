# integrations/price_data_fetcher/utils.py
# version 2.0, aug 2025

from utils.load_configs_and_logs import load_configs_and_logs
from integrations.price_data_fetcher.fetchers.PriceDataFetcher import PriceDataFetcher

def config_and_log_loader():
    
    configs_and_logs = load_configs_and_logs([
        {
            "name": "symbol",
            "mid_folder": "analysis",
            "module_key": "symbol_data_fetcher",
            "extension": ".jsonl",
            "return": ["config", "full_log_path"]
        },
        {
            "name": "module",
            "mid_folder": "fetch",
            "module_key": "price_data_fetcher",
            "extension": ".jsonl",
            "return": ["config", "full_log_path", "full_log_schema_path"]
        }
    ])

    return (
        configs_and_logs["module_full_log_path"],  
        configs_and_logs["module_full_log_schema_path"],
        configs_and_logs["module_config"],
        configs_and_logs["symbol_config"], 
        configs_and_logs["symbol_full_log_path"]
    )

def test_single_exchange(symbol, exchange_name):

    # Module config            
    configs_and_logs = load_configs_and_logs([
        {
            "name": "module",
            "mid_folder": "fetch",
            "module_key": "price_data_fetcher",
            "extension": ".jsonl",
            "return": ["config"] 
        }
    ])

    module_config = configs_and_logs["module_config"]
    general_config = configs_and_logs["general_config"]

    # Run the fetcher
    fetcher = PriceDataFetcher(symbol=symbol, config=module_config, order=[exchange_name])
    data = fetcher.fetch()
    print(f"[TEST] Data from {exchange_name}:", data)