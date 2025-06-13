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

    override_signal = None
    if symbol_args:
        last_arg = symbol_args[-1].lower()
        if last_arg in ["buy", "sell"]:
            override_signal = last_arg
            selected_symbols = selected_symbols[:-1]  # Remove override signal from symbols

    return selected_platform, selected_symbols, override_signal, long_only, short_only
