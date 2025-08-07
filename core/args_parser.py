import sys
import json
from pathlib import Path
from scripts.platform_selection import get_selected_platform
from scripts.symbol_selection import get_selected_symbols

def load_latest_symbols_from_log(log_path: Path):
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
            raise ValueError("No valid JSON lines found in symbol data log.")

    potential_both_ways = latest_entry.get("potential_both_ways", [])
    potential_to_short = latest_entry.get("potential_to_short", [])
    potential_to_long = latest_entry.get("potential_to_long", [])

    seen = set()
    selected_symbols = []

    def add_symbols(symbols):
        for s in symbols:
            if s not in seen:
                seen.add(s)
                selected_symbols.append(s)

    # Prioriteetti: both_ways > short > long
    add_symbols(potential_both_ways)
    add_symbols(potential_to_short)
    add_symbols(potential_to_long)

    return selected_symbols

def parse_arguments():
    args = sys.argv[1:]
    if not args:
        raise ValueError("No arguments provided")

    # Extract trade_mode if specified
    trade_mode = None
    for mode in ["long-only", "short-only", "no-trade", "no-stoploss"]:
        if mode in args:
            trade_mode = mode
            args.remove(mode)
            break

    # Extract override_signal if last arg is 'buy' or 'sell'
    override_signal = args[-1].lower() if args and args[-1].lower() in ["buy", "sell"] else None
    if override_signal:
        args = args[:-1]

    if not args:
        raise ValueError("No platform provided")

    selected_platform = args[0].lower()
    symbol_args = args[1:]

    if not symbol_args:
        log_path = Path("../AI-crypto-trader-logs/analysis-data/symbol_data_log.jsonl")
        selected_symbols = load_latest_symbols_from_log(log_path)
    else:
        selected_symbols = get_selected_symbols(selected_platform, symbol_args)

    return selected_platform, selected_symbols, override_signal, trade_mode
