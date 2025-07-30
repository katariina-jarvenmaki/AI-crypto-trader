# modules/load_and_validate/load_and_validate.py

import os
import json
from jsonschema import validate, ValidationError

default_schema_path = os.path.join(os.path.dirname(__file__), "default_schema.json")

from modules.load_and_validate.utils import read_file, parse_config, load_schema, validate_data

def load_and_validate(file_path="config.json", schema_path=None):
    
    try:
        is_jsonl = file_path.endswith(".jsonl")
        content = read_file(file_path)
        data = parse_config(content, is_jsonl=is_jsonl)

        if schema_path is None:
            schema_path = default_schema_path

        schema = load_schema(schema_path)
        validate_data(data, schema, is_jsonl=is_jsonl)
        return data

    except (FileNotFoundError, ValueError, json.JSONDecodeError, ValidationError) as e:
        print("❌ " + str(e))
    except Exception as e:
        print(f"❌ Tuntematon virhe: {e}")

if __name__ == "__main__":

    result = load_and_validate(
        file_path="../AI-crypto-trader-confs/_TEST/fetch_confs/multi_ohlcv_fetch_config.json", 
        schema_path="../AI-crypto-trader-schemas/_TEST/fetch_schemas/multi_ohlcv_fetch_config_schema.json"
    )
    print(f"✅ File is valid. Result:\n{json.dumps(result, indent=2)}")
