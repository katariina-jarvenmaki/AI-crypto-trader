from modules.pathbuilder.pathbuilder import pathbuilder
from utils.config_reader import config_reader

def run_main_symbols_data_fetcher(general_config_path, general_config_scheme_path):

    print(f"full_config_path: {general_config_path}")
    print(f"full_config_schema_path: {general_config_scheme_path}")

if __name__ == "__main__":

    general_config = config_reader()
    paths = pathbuilder(extension=".jsonl", file_name=general_config["module_filenames"]["symbol_data_fetcher"], mid_folder="analysis")

    run_main_symbols_data_fetcher(paths["full_config_path"], paths["full_config_schema_path"])
