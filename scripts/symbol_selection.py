# scripts/symbol_selection.py

import importlib
import json
import os

def load_recent_symbols_from_log(log_path='symbol_data_log.jsonl'):
    symbols = set()
    if not os.path.exists(log_path):
        return []

    try:
        with open(log_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    symbol = entry.get("symbol")
                    if symbol:
                        symbols.add(symbol.upper())
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Failed to read symbol log file: {e}")
        return []

    return list(symbols)

def get_selected_symbols(platform: str, symbol_args: list):
    config_module_name = f"configs.{platform.lower()}_config"
    try:
        platform_config = importlib.import_module(config_module_name)
    except ImportError:
        raise ImportError(f"Config module '{config_module_name}' not found for platform '{platform}'")

    if not hasattr(platform_config, "SUPPORTED_SYMBOLS") or not hasattr(platform_config, "DEFAULT_SYMBOL"):
        raise AttributeError(f"{config_module_name} is missing SUPPORTED_SYMBOLS or DEFAULT_SYMBOL")

    supported_symbols = platform_config.SUPPORTED_SYMBOLS
    default_symbol = platform_config.DEFAULT_SYMBOL

    # Filter out known non-symbol arguments
    known_non_symbols = {"buy", "sell"}
    filtered_args = [s for s in symbol_args if s.upper() in supported_symbols]

    if not filtered_args:
        # No valid symbols from CLI args: try loading from log file
        recent_symbols = load_recent_symbols_from_log()
        # Filter recent symbols by supported_symbols
        recent_filtered = [s for s in recent_symbols if s in supported_symbols]

        if recent_filtered:
            print(f"Using recent symbols from log: {recent_filtered}")
            return recent_filtered

        # fallback to default symbol
        print(f"No valid symbols found in arguments or logs, falling back to default: {default_symbol}")
        return [default_symbol]

    return filtered_args
