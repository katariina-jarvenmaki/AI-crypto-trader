# utils/load_configs_and_logs.py
# version 2.0, aug 2025

from modules.pathbuilder.pathbuilder import pathbuilder
from modules.load_and_validate.load_and_validate import load_and_validate

def load_configs_and_logs(items, general_config=None):
    """
    items: List of dict
        [
            {
                "name": "symbol",
                "mid_folder": "analysis",
                "module_key": "symbol_data_fetcher",
                "extension": ".jsonl",
                "return": ["config", "full_log_path", "full_temp_log_path"]
            },
            ...
        ]
    """
    if general_config is None:
        general_config = load_and_validate()

    results = {"general_config": general_config}

    for item in items:
        file_name = general_config["module_filenames"][item["module_key"]]
        paths = pathbuilder(
            extension=item.get("extension", ".jsonl"),
            file_name=file_name,
            mid_folder=item["mid_folder"]
        )

        for key in item["return"]:
            if key == "config":
                config = load_and_validate(
                    file_path=paths["full_config_path"],
                    schema_path=paths["full_config_schema_path"]
                )
                results[f"{item['name']}_config"] = config
            elif key in paths:
                results[f"{item['name']}_{key}"] = paths[key]
            else:
                raise KeyError(f"Requested return key '{key}' not found in pathbuilder result.")

    return results

if __name__ == "__main__":
    
    configs_and_logs = load_configs_and_logs([
        {
            "name": "symbol",
            "mid_folder": "analysis",
            "module_key": "symbol_data_fetcher",
            "extension": ".jsonl",
            "return": ["config", "full_log_path", "full_temp_log_path"]
        },
        {
            "name": "module",
            "mid_folder": "fetch",
            "module_key": "price_data_fetcher",
            "extension": ".jsonl",
            "return": ["configs_path", "logs_path", "schemas_path", "log_schema", "full_config_path"]
        }
    ])

    for k, v in configs_and_logs.items():
        print(f"{k}: {v}")
