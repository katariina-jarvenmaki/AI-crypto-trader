
# modules/history_analyzer/utils.py

import json
from typing import List
from modules.history_analyzer.config_history_analyzer import CONFIG

import json
from typing import List
from modules.history_analyzer.config_history_analyzer import CONFIG

def get_latest_symbols_from_log(file_path: str) -> List[str]:
    with open(file_path, "r") as f:
        lines = f.readlines()
        if not lines:
            return []
        last_line = lines[-1].strip()
        try:
            last_entry = json.loads(last_line)
        except json.JSONDecodeError:
            decoder = json.JSONDecoder()
            last_entry, _ = decoder.raw_decode(last_line)

        combined_symbols = set()
        for key in CONFIG["symbol_keys"]:
            combined_symbols.update(last_entry.get(key, []))

        return list(combined_symbols)

