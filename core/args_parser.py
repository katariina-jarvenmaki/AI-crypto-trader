# core/args_parser.py

import sys
from scripts.platform_selection import get_selected_platform
from scripts.symbol_selection import get_selected_symbols

def parse_arguments():
    args = sys.argv[1:]
    if not args:
        raise ValueError("No arguments provided")

    # Flags
    long_only = "long-only" in args
    short_only = "short-only" in args

    # Remove known flags from args for further parsing
    args = [arg for arg in args if arg not in ["long-only", "short-only"]]

    selected_platform = get_selected_platform(args)
    symbol_args = args[1:] if selected_platform.lower() == args[0].lower() else args
    selected_symbols = get_selected_symbols(selected_platform, symbol_args)

    override_signal = args[-1].lower() if args[-1].lower() in ["buy", "sell"] else None

    return selected_platform, selected_symbols, override_signal, long_only, short_only
