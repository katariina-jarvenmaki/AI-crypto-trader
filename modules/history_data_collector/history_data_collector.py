
from typing import List
from utils.get_timestamp import get_timestamp
from modules.pathbuilder.pathbuilder import pathbuilder
from utils.get_symbols_to_use import get_symbols_to_use
from modules.load_and_validate.load_and_validate import load_and_validate
from utils.load_latest_entries_per_symbol import load_latest_entries_per_symbol

def history_data_collector(symbols: List[str]):

    seen = set()
    parsed_entries = []
    # price_data_entries = load_latest_entries_per_symbol(symbols, CONFIG["price_log_path"], max_age_minutes=10**9)
    # print(price_data_entries)

if __name__ == "__main__":

    timestamp = get_timestamp()
    print(f"\n🕒 Running history data collector at: {timestamp}\n")

    general_config = load_and_validate()
    
    symbol_paths = pathbuilder(
        extension=".jsonl", 
        file_name=general_config["module_filenames"]["symbol_data_fetcher"], 
        mid_folder="analysis"
    )

    module_log_path = symbol_paths["full_log_path"]
    module_schema_path = symbol_paths["full_log_schema_path"]
    module_config = load_and_validate(
        file_path=symbol_paths["full_config_path"],
        schema_path=symbol_paths["full_config_schema_path"]
    )

    result = get_symbols_to_use(module_config, module_log_path)
    all_symbols = result["all_symbols"]

    history_data_collector(all_symbols)
