
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

def format_value(val):
    if val == 0:
        return "0.000"

    abs_val = abs(val)
    s = f"{val:.15f}"  # riittävän pitkä desimaaliosa

    if abs_val >= 1:
        return f"{val:.3f}"

    integer_part, decimal_part = s.split('.')

    # Lasketaan etunollat desimaaliosassa
    leading_zeros = 0
    for c in decimal_part:
        if c == '0':
            leading_zeros += 1
        else:
            break

    # Tarvittavat desimaalit = nollat + 3 desimaalia nollien jälkeen
    needed_len = leading_zeros + 3

    # Täydennetään nollilla, jos decimal_part liian lyhyt
    if len(decimal_part) < needed_len:
        decimal_part += '0' * (needed_len - len(decimal_part))
    else:
        decimal_part = decimal_part[:needed_len]

    return f"{integer_part}.{decimal_part}"

def decimals_in_number(num):
    s = str(num)
    if '.' in s:
        return len(s.split('.')[1])
    return 0
