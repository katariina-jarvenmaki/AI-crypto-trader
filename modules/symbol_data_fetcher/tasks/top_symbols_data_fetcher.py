from modules.pathbuilder.pathbuilder import pathbuilder
from modules.load_and_validate.load_and_validate import load_and_validate 

def run_top_symbols_data_fetcher(general_config, module_config):

    print(f"general_config: {general_config}")
    print(f"module_config: {module_config}")

if __name__ == "__main__":

    general_config = load_and_validate()
    paths = pathbuilder(extension=".json", file_name=general_config["module_filenames"]["symbol_data_fetcher"], mid_folder="analysis")

    module_config = load_and_validate(file_path=paths["full_config_path"], schema_path=paths["full_config_schema_path"])

    run_top_symbols_data_fetcher(general_config, module_config)
