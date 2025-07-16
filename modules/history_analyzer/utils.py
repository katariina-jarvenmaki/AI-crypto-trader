
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

# For text formating only price
def format_change_for_price_data(current, prev, label):

    if current is None or prev is None:
        return f"{label}: {current} (ei vertailuarvoa)"

    decimals = decimals_in_number(current)
    fmt = f"{{:.{decimals}f}}"
    current_fmt = fmt.format(current)
    prev_fmt = fmt.format(prev)

    delta = current - prev
    delta_fmt = format_value(delta)

    perc = (delta / prev) * 100 if prev != 0 else 0
    sign = "+" if delta > 0 else ""

    return (
        f"{label}: ${current_fmt} vs ${prev_fmt} "
        f"({sign}${delta_fmt}, {sign}{perc:.2f}%)"
    )

# For text formating only price
def format_change(current, prev, label):
    def format_value(val):
        s = f"{val:.15f}".rstrip('0').rstrip('.')
        abs_val = abs(val)

        if abs_val >= 1:
            # Pyöristetään 3 desimaaliin normaalisti
            return f"{val:.3f}"

        # Ota desimaaliosa
        if '.' not in s:
            return "0.000"
        integer_part, decimal_part = s.split('.')

        # Lasketaan nollat desimaalien alussa
        leading_zeros = 0
        for c in decimal_part:
            if c == '0':
                leading_zeros += 1
            else:
                break

        needed_len = leading_zeros + 3

        if len(decimal_part) < needed_len:
            decimal_part += '0' * (needed_len - len(decimal_part))
        else:
            decimal_part = decimal_part[:needed_len]

        return f"{integer_part}.{decimal_part}"

    fmt = format_value

    if current is None or prev is None:
        return f"{label}: {fmt(current)} (ei vertailuarvoa)"

    delta = current - prev
    perc = (delta / prev) * 100 if prev != 0 else 0
    sign = "+" if delta > 0 else ""

    return (
        f"{label}: {fmt(current)} vs {fmt(prev)} "
        f"({sign}{fmt(delta)}, {sign}{perc:.2f}%)"
    )