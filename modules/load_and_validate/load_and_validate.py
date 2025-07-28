# modules/load_and_validate/load_and_validate.py

import json
import os
from jsonschema import validate, ValidationError

DEFAULT_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "default_schema.json")

def load_and_validate(path="config.json", schema=None):

    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Config file not found at: {path}")

    is_jsonl = path.endswith(".jsonl")

    # Read file content first
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        raise ValueError(f"❌ Config file is empty: {path}")

    # Parse content
    if is_jsonl:
        file_data = [json.loads(line) for line in content.splitlines() if line.strip()]
    else:
        file_data = json.loads(content)

    # Load JSON or JSONL file
    with open(path, "r", encoding="utf-8") as f:
        if is_jsonl:
            file_data = [json.loads(line) for line in f if line.strip()]
        else:
            file_data = json.load(f)

    # Determine which schema to use
    if schema is None:
        if os.path.exists(DEFAULT_SCHEMA_PATH):
            with open(DEFAULT_SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema = json.load(f)
        else:
            raise FileNotFoundError(
                f"Default schema not found at: {DEFAULT_SCHEMA_PATH}. "
                f"Provide schema explicitly as a parameter."
            )
    elif isinstance(schema, str) and schema.endswith(".json") and os.path.exists(schema):
        with open(schema, "r", encoding="utf-8") as f:
            schema = json.load(f)
    else:
        raise ValueError("Invalid schema parameter: must be a path to a .json file")

    # Validation
    try:
        if is_jsonl:
            for i, item in enumerate(file_data):
                try:
                    validate(instance=item, schema=schema)
                except ValidationError as e:
                    print(f"❌ JSONL validation failed on line {i+1}:\n→ {e.message}")
                    raise
        else:
            validate(instance=file_data, schema=schema)
    except ValidationError:
        raise

    return file_data

if __name__ == "__main__":
    result = load_and_validate()
    print(f"✅ File is valid. Result:\n{json.dumps(result, indent=2)}")
