from modules.pathbuilder.pathbuilder import pathbuilder
from utils.config_reader import config_reader

def run_top_symbols_data_fetcher(general_config, module_config):

    print(f"general_config: {general_config}")
    print(f"module_config: {module_config}")

if __name__ == "__main__":

    general_config = config_reader()
    paths = pathbuilder(extension=".json", file_name=general_config["module_filenames"]["symbol_data_fetcher"], mid_folder="analysis")

    module_config = config_reader(config_path=paths["full_config_path"], schema_path=paths["full_config_schema_path"])

    run_top_symbols_data_fetcher(general_config, module_config)
