# utils/get_filenames.py

from pathlib import Path

def get_filenames(extension=".json"):
    """
    Returns three filenames based on the name of the parent folder:
    - config name: <folder>_config.json
    - log name: <folder>_log.<extension>
    - temp log name: temp_log_<folder>.<extension>
    """
    # Get the absolute path of this script
    caller_path = Path(__file__).resolve()

    # Get the name of the parent folder
    parent_folder_name = caller_path.parent.name

    # Construct filenames
    config_name = f"{parent_folder_name}_config.json"
    log_name = f"{parent_folder_name}_log{extension}"
    temp_log_name = f"temp_log_{parent_folder_name}{extension}"

    return config_name, log_name, temp_log_name

# Example usage
if __name__ == "__main__":
    config, log, temp_log = get_filenames(extension=".jsonl")
    print("Config filename:", config)
    print("Log filename:", log)
    print("Temp log filename:", temp_log)
