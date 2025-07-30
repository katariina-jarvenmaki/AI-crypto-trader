import os
import json
from pathlib import Path
from jsonschema import validate, ValidationError
from modules.save_and_validate.truncate_file_if_too_large import truncate_file_if_too_large

def save_and_validate(data=None, path: str = None, schema: dict = None):
    """
    Tallentaa annetun datan JSON- tai JSONL-muotoon.
    Tarkistaa, että data ja path on annettu.
    Jos tiedosto on olemassa, validoi sen. Jos validointi epäonnistuu tai tiedostoa ei ole,
    luo hakemisto tarvittaessa ja kirjoittaa uuden tiedoston.
    Lopuksi tallentaa annetun datan tiedostoon.
    """

    if data is None:
        raise ValueError("❌ Data argument is missing or with no value.")
    if path is None:
        raise ValueError("❌ Path argument is missing or with no value.")
    if schema is None:
        raise ValueError("❌ Schema argument is missing or with no value.")

    if isinstance(schema, str) and os.path.isfile(schema):
        with open(schema, "r", encoding="utf-8") as f:
            schema = json.load(f)

    is_jsonl = path.endswith(".jsonl")
    dir_path = os.path.dirname(path)

    file_exists = os.path.exists(path)
    file_valid = False

    # 🔍 1. Jos tiedosto on olemassa, yritetään validoida
    if file_exists:
        truncate_file_if_too_large(Path(path))
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                print(f"📄 File is empty, skipping validation: {path}")
                file_valid = True
            else:
                file_data = (
                    [json.loads(line) for line in content.splitlines() if line.strip()]
                    if is_jsonl else json.loads(content)
                )

                if schema:
                    if is_jsonl:
                        for i, item in enumerate(file_data):
                            validate(instance=item, schema=schema)
                    else:
                        validate(instance=file_data, schema=schema)

                file_valid = True
                print(f"✅ Existing file is valid: {path}")

        except (json.JSONDecodeError, ValidationError) as e:
            print(f"⚠️ Existing file is invalid → will be overwritten:\n→ {e}")
            file_valid = False

    # 🛠 2. Jos tiedostoa ei ole tai se oli virheellinen → luodaan polku ja tyhjä tiedosto
    if not file_exists or not file_valid:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"📁 Created directory: {dir_path}")

        with open(path, "w", encoding="utf-8") as f:
            pass

        print(f"💾 Created or replaced file at: {path}")

    # ✍️ 3. Tallennetaan annettu data tiedostoon
    with open(path, "a" if is_jsonl else "w", encoding="utf-8") as f:
        if is_jsonl:
            if isinstance(data, list):
                for item in data:
                    f.write(json.dumps(item) + "\n")
            else:
                f.write(json.dumps(data) + "\n")
        else:
            json.dump(data, f, indent=2)

    print(f"📦 Data saved to: {path}")

    return True

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

    print("✅ Done")

