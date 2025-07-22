import os
import json
from integrations.bybit_api_client import client as bybit_client

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config_positions_data_fetcher.json")

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

config = load_config()
LOG_FILE_PATH = config["log_file_path"]

def ensure_log_file_exists():
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "w") as f:
            json.dump([], f)

def is_log_file_empty():
    return os.path.getsize(LOG_FILE_PATH) == 0

def log_positions(positions):
    clean_positions = []

    for pos in positions:
        try:
            clean_pos = {k: v for k, v in pos.items()}
            clean_positions.append(clean_pos)
        except Exception:
            pass  # Virheet ohitetaan hiljaa

    with open(LOG_FILE_PATH, "w") as f:
        json.dump(clean_positions, f, indent=2)

    return clean_positions

def fetch_all_positions_bybit():
    all_positions = []
    cursor = None

    while True:
        params = {
            "category": config["bybit"]["category"],
            "settleCoin": config["bybit"]["settle_coin"],
            "limit": config["bybit"]["limit"]
        }
        if cursor:
            params["cursor"] = cursor

        try:
            response = bybit_client.get_positions(**params)
            result = response.get("result", {})
            positions = result.get("list", [])
            all_positions.extend(positions)
            cursor = result.get("nextPageCursor")
            if not cursor:
                break
        except Exception:
            break  # Epäonnistuminen katkaisee haun

    return all_positions

def position_data_fetcher():
    ensure_log_file_exists()
    positions = fetch_all_positions_bybit()
    logged_data = log_positions(positions)
    return logged_data
