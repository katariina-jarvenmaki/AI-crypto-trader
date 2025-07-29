# utils/path_selector.py
# Use with prints:    configs_path, logs_path, schemas_path = path_selector()
# Use without prints: configs_path, logs_path, schemas_path = path_selector(verbose=False)

from modules.load_and_validate.load_and_validate import load_and_validate

def path_selector(verbose=True, mid_folder=None):

    allowed_mid_folders = {"cron", "analysis", "fetch", "order", "signal"}

    if verbose:
        print("Running Path Selector...")

    if mid_folder and mid_folder not in allowed_mid_folders:
        raise ValueError(f"Invalid mid_folder: '{mid_folder}'. Must be one of {allowed_mid_folders}")

    # Load config
    result = load_and_validate()
    testing = result["testing"]

    if testing:
        base_configs_path = result["paths"]["configs"]["test"]
        base_logs_path = result["paths"]["logs"]["test"]
        base_schemas_path = result["paths"]["schemas"]["test"]
    else:
        base_configs_path = result["paths"]["configs"]["live"]
        base_logs_path = result["paths"]["logs"]["live"]
        base_schemas_path = result["paths"]["schemas"]["live"]

    # Append mid_folder suffixes if provided
    if mid_folder:
        configs_path = base_configs_path + f"{mid_folder}_confs/"
        logs_path = base_logs_path + f"{mid_folder}_logs/"
        schemas_path = base_schemas_path + f"{mid_folder}_schemas/"
    else:
        configs_path = base_configs_path
        logs_path = base_logs_path
        schemas_path = base_schemas_path

    return configs_path, logs_path, schemas_path

if __name__ == "__main__":

    configs_path, logs_path, schemas_path = path_selector(verbose=True, mid_folder="cron")
    # configs_path, logs_path, schemas_path = path_selector(verbose=False)

    print(f"Configs: {configs_path}")
    print(f"Logs: {logs_path}")
    print(f"Schemas: {schemas_path}")
