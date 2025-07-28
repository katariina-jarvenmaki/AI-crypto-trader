# integrations/multi_interval_ohlcv/multi_ohlcv_handler.py

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from utils.path_selector import path_selector
from utils.get_filenames import get_filenames

# Defining config and log paths
configs_path, logs_path, schemas_path = path_selector(verbose=False, mid_folder="fetch")
config, log, temp_log, schemas = get_filenames(extension=".jsonl", file_name="multi_ohlcv_fetch")

def multi_ohlcv_handler():
    print(f"configs_path: {configs_path}{config}")
    print(f"logs_path: {logs_path}{log}")
    print(f"logs_path: {logs_path}{temp_log}")
    print(f"schemas_path: {schemas_path}{schemas}")

if __name__ == "__main__":
    multi_ohlcv_handler()
