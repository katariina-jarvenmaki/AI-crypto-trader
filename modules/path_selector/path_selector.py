# modules/path_selector/path_selector.py
# Use with prints:    configs_path, logs_path = path_selector()
# Use without prints: configs_path, logs_path = path_selector(verbose=False)

from modules.load_and_validate.load_and_validate import load_and_validate

def path_selector(verbose=True):

    if verbose:
        print("Running Path Selector...")

    # Load config
    result = load_and_validate()
    testing = result["testing"]

    if testing:
        configs_path = result["paths"]["configs"]["test"]
        logs_path = result["paths"]["logs"]["test"]
    else:
        configs_path = result["paths"]["configs"]["live"]
        logs_path = result["paths"]["logs"]["live"]

    return configs_path, logs_path

if __name__ == "__main__":

    configs_path, logs_path = path_selector()
    # configs_path, logs_path = path_selector(verbose=False)
    print(f"Configs: {configs_path}")
    print(f"Logs: {logs_path}")
