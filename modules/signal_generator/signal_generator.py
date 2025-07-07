# modules/symbol_data_fetcher/symbol_data_fetcher.py

import argparse
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from modules.symbol_data_fetcher.tasks.potential_trades_checker import run_potential_trades_checker
from modules.symbol_data_fetcher.tasks.top_symbols_data_fetcher import run_top_symbols_data_fetcher
from modules.symbol_data_fetcher.tasks.main_symbols_data_fetcher import run_main_symbols_data_fetcher

sys.path.append(str(Path(__file__).resolve().parents[2]))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():

    parser = argparse.ArgumentParser(
        description="Symbol Data Fetcher - executes various background tasks for market data analysis."
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Potential traders (every 2 days)
    parser_potential = subparsers.add_parser("potential_trades_checker", help="Run potential traders check")
    parser_potential.set_defaults(func=run_potential_trades_checker)

    # Supported symbols (every 30 minutes)
    parser_supported = subparsers.add_parser("top_symbols_data_fetcher", help="Fetch supported symbols data")
    parser_supported.set_defaults(func=run_top_symbols_data_fetcher)

    # Main symbols data (every 5 minutes)
    parser_main = subparsers.add_parser("main_symbols_data_fetcher", help="Fetch main symbols data")
    parser_main.set_defaults(func=run_main_symbols_data_fetcher)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func()

if __name__ == "__main__":
    main()
