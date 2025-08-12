# modules/load_and_validate/utils.py
# version 2.0, aug 2025

import os
import json
from jsonschema import validate, ValidationError

def read_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ File not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        raise ValueError(f"❌ File is empty: {path}")

    return content


def parse_config(content, is_jsonl=False):
    try:
        if is_jsonl:
            return [json.loads(line) for line in content.splitlines() if line.strip()]
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"❌ JSON parsing failed: {str(e)}", content, e.pos)


def load_schema(schema_path=None):
    if schema_path is None:
        schema_path = default_schema_path

    if not os.path.exists(schema_path):
        raise FileNotFoundError(
            f"❌ Schema file not found at: {schema_path}. "
            f"Provide schema explicitly or ensure default exists."
        )

    with open(schema_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"❌ Schema JSON parsing failed: {str(e)}", f.read(), e.pos)


def validate_data(data, schema, is_jsonl=False):
    if is_jsonl:
        for i, item in enumerate(data):
            try:
                validate(instance=item, schema=schema)
            except ValidationError as e:
                raise ValidationError(f"❌ JSONL validation failed on line {i + 1}:\n→ {e.message}")
    else:
        validate(instance=data, schema=schema)