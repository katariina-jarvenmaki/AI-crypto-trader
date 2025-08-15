# tests/test_save_and_validate.py
import json
import tempfile
import os
from modules.save_and_validate.save_and_validate import save_and_validate

# Dummy schema, vaatii symbolin ja timestampin
schema = {
    "type": "object",
    "properties": {
        "symbol": {"type": "string"},
        "timestamp": {"type": "string"}
    },
    "required": ["symbol", "timestamp"]
}

def test_correct_format_saves_ok():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tmp:
        path = tmp.name
    data = {"symbol": "BTCUSDT", "timestamp": "2025-08-14T10:00:00"}
    save_and_validate(data=data, path=path, schema=schema, verbose=False)

    with open(path) as f:
        lines = [json.loads(line) for line in f]
    assert lines[0]["symbol"] == "BTCUSDT"

    os.remove(path)

def test_old_format_is_fixed():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tmp:
        path = tmp.name
    data = {"BTCUSDT": {"timestamp": "2025-08-14T10:00:00"}}
    save_and_validate(data=data, path=path, schema=schema, verbose=False)

    with open(path) as f:
        lines = [json.loads(line) for line in f]
    assert lines[0]["symbol"] == "BTCUSDT"

    os.remove(path)

def test_mixed_list_saves_ok():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tmp:
        path = tmp.name
    data = [
        {"symbol": "ETHUSDT", "timestamp": "2025-08-14T10:00:00"},
        {"XRPUSDT": {"timestamp": "2025-08-14T10:00:00"}}
    ]
    save_and_validate(data=data, path=path, schema={"type": "array", "items": schema}, verbose=False)

    with open(path) as f:
        lines = [json.loads(line) for line in f]
    assert lines[0]["symbol"] == "ETHUSDT"
    assert lines[1]["symbol"] == "XRPUSDT"

    os.remove(path)
