from pathlib import Path

def get_filenames(extension=".json", file_name=None):
    """
    Returns four filenames based on the given file name or the name of the parent folder:
    - config name: <name>_config.json
    - log name: <name>_log.<extension>
    - temp log name: temp_log_<name>.<extension>
    - schemas name: <name>_schemas.json

    Parameters:
    - extension (str): File extension (e.g. '.json' or '.jsonl')
    - file_name (str or None): Optional override for the folder name
    """
    # Use the provided file_name or fallback to the parent folder of this file
    if file_name is None:
        caller_path = Path(__file__).resolve()
        file_name = caller_path.parent.name

    # Construct filenames
    config_name = f"{file_name}_config.json"
    log_name = f"{file_name}_log{extension}"
    temp_log_name = f"temp_log_{file_name}{extension}"
    schemas_name = f"{file_name}_schemas.json"

    return config_name, log_name, temp_log_name, schemas_name

# Example usage
if __name__ == "__main__":
    config, log, temp_log, schemas = get_filenames(extension=".jsonl")
    print("\nWithout name override:")
    print("Config filename:", config)
    print("Log filename:", log)
    print("Temp log filename:", temp_log)
    print("Schemas filename:", schemas)

    print("\nWith name override:")
    config, log, temp_log, schemas = get_filenames(extension=".json", file_name="customproject")
    print("Config filename:", config)
    print("Log filename:", log)
    print("Temp log filename:", temp_log)
    print("Schemas filename:", schemas)

    print("")
