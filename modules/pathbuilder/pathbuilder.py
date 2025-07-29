
from modules.pathbuilder.path_selector import path_selector
from modules.pathbuilder.get_filenames import get_filenames

def pathbuilder(extension=".json", file_name=None, mid_folder=None):

    # Defining config and log paths
    configs_path, logs_path, schemas_path = path_selector(verbose=False, mid_folder=mid_folder)
    config, log, temp_log, schemas = get_filenames(extension=extension, file_name=file_name)

    full_config_path = configs_path + config
    full_log_path = logs_path + log
    full_temp_log_path = logs_path + temp_log
    full_schema_path = schemas_path + schemas

    return {
        "configs_path": configs_path,
        "logs_path": logs_path,
        "schemas_path": schemas_path,
        "config": config,
        "log": log,
        "temp_log": temp_log,
        "schemas": schemas,
        "full_config_path": full_config_path,
        "full_log_path": full_log_path,
        "full_temp_log_path": full_temp_log_path,
        "full_schema_path": full_schema_path,
    }

if __name__ == "__main__":
    
    result = pathbuilder(extension=".json", file_name="multi_ohlcv_fetch", mid_folder="fetch")
    print(f"result: {result}")