# scripts/utils.py

import json
from pathlib import Path

def load_symbol_modes(symbols, long_only_flag, short_only_flag):
    
    log_path = Path("../AI-crypto-trader-logs/analysis-data/symbol_data_log.jsonl")

    with open(log_path, "r") as f:
        lines = f.readlines()
        if not lines:
            raise ValueError(f"No data in {log_path}")

        for line in reversed(lines):
            try:
                latest_entry = json.loads(line.strip())
                break
            except json.JSONDecodeError:
                continue
        else:
            raise ValueError("No valid JSON in symbol log")

    potential_both_ways = latest_entry.get("potential_both_ways", [])
    potential_to_short = latest_entry.get("potential_to_short", [])
    potential_to_long = latest_entry.get("potential_to_long", [])

    symbol_modes = {}

    for symbol in symbols:
        if symbol in potential_to_short:
            symbol_modes[symbol] = {"long_only": False, "short_only": True}
        elif symbol in potential_to_long:
            symbol_modes[symbol] = {"long_only": True, "short_only": False}
        elif symbol in potential_both_ways:
            symbol_modes[symbol] = {
                "long_only": long_only_flag,
                "short_only": short_only_flag
            }
        else:
            # Jos symboli ei ole missään listassa, ei rajoituksia
            symbol_modes[symbol] = {"long_only": False, "short_only": False}

    return symbol_modes