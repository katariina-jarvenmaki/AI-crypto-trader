import os
import json
from pathlib import Path
from jsonschema import validate, ValidationError
from modules.save_and_validate.file_checker import file_checker

def save_and_validate(data=None, path: str = None, schema: dict = None):

    if data is None:
        raise ValueError("❌ Data argument is missing.")
    if path is None:
        raise ValueError("❌ Path argument is missing.")
    if schema is None:
        raise ValueError("❌ Schema argument is missing.")

    # Jos skeema on tiedostopolku, ladataan se
    if isinstance(schema, str) and os.path.isfile(schema):
        with open(schema, "r", encoding="utf-8") as f:
            schema = json.load(f)

    # 🔁 Uusi korvaava validointilogiikka
    file_checker(path)

    is_jsonl = path.endswith(".jsonl")

    # ✍️ Tallenna data tiedostoon
    with open(path, "a" if is_jsonl else "w", encoding="utf-8") as f:
        if is_jsonl:
            if isinstance(data, list):
                for item in data:
                    validate(instance=item, schema=schema)
                    f.write(json.dumps(item) + "\n")
            else:
                validate(instance=data, schema=schema)
                f.write(json.dumps(data) + "\n")
        else:
            validate(instance=data, schema=schema)
            json.dump(data, f, indent=2)

    print(f"📦 Data saved to: {path}")

if __name__ == "__main__":

    import json
    from modules.pathbuilder.pathbuilder import pathbuilder
    from utils.config_reader import config_reader

    general_config = config_reader()
    paths = pathbuilder(extension=".json", file_name=general_config["module_filenames"]["multi_interval_ohlcv"], mid_folder="fetch")

    jsonl = {
        "timestamp": "2025-07-30T10:46:31.708804",
        "source_exchange": "Okx",
        "symbol": "BTCUSDT",
        "intervals": ["1h", "4h"],
        "data_preview": {
            "1h": {
                "rsi": 52.61, "ema": 118038.6, "macd": -41.02,
                "macd_signal": -109.49, "bb_upper": 118655.48,
                "bb_lower": 117197.54, "close": 118199.1
            },
            "4h": {
                "rsi": 50.12, "ema": 118199.61, "macd": -9.22,
                "macd_signal": 62.2, "bb_upper": 119472.02,
                "bb_lower": 117344.15, "close": 118199.1
            }
        },
        "limit": 500,
        "start_time": None,
        "end_time": None
    }

    general_config = config_reader()
    paths = pathbuilder(
        extension=".jsonl",
        file_name=general_config["module_filenames"]["multi_interval_ohlcv"],
        mid_folder="fetch"
    )

    save_and_validate(data=jsonl, path=paths["full_log_path"], schema=paths["full_log_schema_path"])


