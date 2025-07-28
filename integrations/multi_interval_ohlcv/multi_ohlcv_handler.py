# integrations/multi_interval_ohlcv/multi_ohlcv_handler.py

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from utils.config_reader import config_reader

def multi_ohlcv_handler():

    config=config_reader(extension=".json", file_name="multi_ohlcv_fetch", mid_folder="fetch")
    print(f"config: {config}")

if __name__ == "__main__":
    multi_ohlcv_handler()
