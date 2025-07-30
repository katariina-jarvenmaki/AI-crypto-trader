# modules/load_and_validate/load_and_validate.py

# import json
import os
# from jsonschema import validate, ValidationError

import os
import json
from jsonschema import validate, ValidationError

def save_and_validate(data=None, path: str = None, schema: dict = None):
    """
    Tallentaa annetun datan JSON- tai JSONL-muotoon.
    Tarkistaa, että data ja path on annettu.
    Jos tiedosto on olemassa, validoi sen. Jos validointi epäonnistuu tai tiedostoa ei ole,
    luo hakemisto tarvittaessa ja kirjoittaa uuden tiedoston.
    """

    if data is None:
        raise ValueError("❌ Data argument is missing or with no value.")
    if path is None:
        raise ValueError("❌ Path argument is missing or with no value.")

    is_jsonl = path.endswith(".jsonl")
    dir_path = os.path.dirname(path)

    file_exists = os.path.exists(path)
    file_valid = False

    # 🔍 1. Jos tiedosto on olemassa, yritetään validoida
    if file_exists:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                raise ValueError(f"❌ File is empty: {path}")

            file_data = (
                [json.loads(line) for line in content.splitlines() if line.strip()]
                if is_jsonl
                else json.loads(content)
            )

            # Validoidaan, jos schema on annettu
            if schema:
                if is_jsonl:
                    for i, item in enumerate(file_data):
                        validate(instance=item, schema=schema)
                else:
                    validate(instance=file_data, schema=schema)

            file_valid = True
            print(f"✅ Existing file is valid: {path}")

        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            print(f"⚠️ Existing file is invalid → will be overwritten:\n→ {e}")
            file_valid = False

    # 🛠 2. Jos tiedostoa ei ole tai se oli virheellinen → luodaan polku ja kirjoitetaan uusi tiedosto
    if not file_exists or not file_valid:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"📁 Created directory: {dir_path}")

        with open(path, "w", encoding="utf-8") as f:
            if is_jsonl:
                json.dump(data, f)
                f.write("\n")
            else:
                json.dump(data, f, indent=2)

        print(f"💾 Created or replaced file at: {path}")



    # Parse content
    # if is_jsonl:
    #     file_data = [json.loads(line) for line in content.splitlines() if line.strip()]
    # else:
    #     file_data = json.loads(content)

    # Load JSON or JSONL file
    # with open(path, "r", encoding="utf-8") as f:
    #     if is_jsonl:
    #         file_data = [json.loads(line) for line in f if line.strip()]
    #     else:
    #         file_data = json.load(f)

    # Determine which schema to use
    # if schema is None:
    #     if os.path.exists(DEFAULT_SCHEMA_PATH):
    #         with open(DEFAULT_SCHEMA_PATH, "r", encoding="utf-8") as f:
    #             schema = json.load(f)
    #     else:
    #         raise FileNotFoundError(
    #             f"Default schema not found at: {DEFAULT_SCHEMA_PATH}. "
    #             f"Provide schema explicitly as a parameter."
    #         )
    # elif isinstance(schema, str) and schema.endswith(".json") and os.path.exists(schema):
    #     with open(schema, "r", encoding="utf-8") as f:
    #         schema = json.load(f)
    # else:
    #     raise ValueError("Invalid schema parameter: must be a path to a .json file")

    # Validation
    # try:
    #     if is_jsonl:
    #         for i, item in enumerate(file_data):
    #             try:
    #                 validate(instance=item, schema=schema)
    #             except ValidationError as e:
    #                 print(f"❌ JSONL validation failed on line {i+1}:\n→ {e.message}")
    #                 raise
    #     else:
    #         validate(instance=file_data, schema=schema)
    # except ValidationError:
    #     raise

    # return file_data

if __name__ == "__main__":

    import json
    from modules.pathbuilder.pathbuilder import pathbuilder
    from utils.config_reader import config_reader

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

    save_and_validate(data=jsonl, path=paths["full_log_path"], schema=schema)

    print("✅ Done")

