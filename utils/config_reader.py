# modules/load_and_validate/load_and_validate.py
import json
from utils.path_selector import path_selector
from utils.get_filenames import get_filenames
from modules.load_and_validate.load_and_validate import load_and_validate

def config_reader(extension=".json", file_name=None, mid_folder=None):
    
    try:
        # Defining config and log paths
        configs_path, logs_path, schemas_path = path_selector(verbose=False, mid_folder=mid_folder)
        config, log, temp_log, schemas = get_filenames(extension=extension, file_name=file_name)
        filepath = configs_path + config

        # Attempt to load and validate
        result = load_and_validate(path=filepath)
        return result

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(str(e))
    except Exception as e:
        print(f"❌ Tuntematon virhe: {e}")

if __name__ == "__main__":
    config_reader(extension=".json", file_name="multi_ohlcv_fetch", mid_folder="fetch")
