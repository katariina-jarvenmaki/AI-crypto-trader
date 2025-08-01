# modules/save_and_validate/save_and_validate.py

import os
import json
from pathlib import Path
from jsonschema import validate, ValidationError
from modules.save_and_validate.file_checker import file_checker

def save_and_validate(data=None, path: str = None, schema: dict = None, verbose=True):

    if data is None:
        raise ValueError("❌ Data argument is missing.")
    if path is None:
        raise ValueError("❌ Path argument is missing.")
    if schema is None:
        raise ValueError("❌ Schema argument is missing.")

    # Jos skeema on tiedostopolku, ladataan se
    if isinstance(schema, str) and os.path.isfile(schema):
        with open(schema, "r", encoding="utf-8") as f:
            try:
                schema = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"❌ Failed to parse schema at {schema_path}: {e}")
            
            if not isinstance(schema, (dict, bool)):
                raise TypeError(f"❌ Invalid schema type: {type(schema)}. Expected dict or bool.")

    # 🔁 Uusi korvaava validointilogiikka
    file_checker(path, verbose=verbose)

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

    if verbose:
        print(f"📦 Data saved to: {path}")

if __name__ == "__main__":

    from modules.pathbuilder.pathbuilder import pathbuilder
    from modules.load_and_validate.load_and_validate import load_and_validate

    # Lataa ja tarkista konfiguraatio
    general_config = load_and_validate()
    if general_config is None:
        raise RuntimeError("❌ general_config is None — config loading or validation failed.")

    # Rakenna polut
    paths = pathbuilder(
        extension=".jsonl",
        file_name=general_config["module_filenames"]["multi_interval_ohlcv"],
        mid_folder="fetch"
    )

    # Esimerkkidata
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

    # Tallenna ja validoi
    save_and_validate(data=jsonl, path=paths["full_log_path"], schema=paths["full_log_schema_path"])
