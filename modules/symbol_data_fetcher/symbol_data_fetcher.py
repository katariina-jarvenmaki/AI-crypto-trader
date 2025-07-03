# modules/symbol_data_fetcher/symbol_data_fetcher.py

import argparse
import logging
import sys

from pathlib import Path
from tasks.potential_trades_checker import run_potential_trades_checker
from tasks.supported_symbols_data_fetcher import run_supported_symbols_data_fetcher
from tasks.main_symbols_data_fetcher import run_main_symbols_data_fetcher

sys.path.append(str(Path(__file__).resolve().parents[2]))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():

    parser = argparse.ArgumentParser(
        description="Symbol Data Fetcher - suorittaa eri taustatehtäviä markkinadata-analyysille."
    )
    subparsers = parser.add_subparsers(dest="command", help="Komennot")

    # Potentiaaliset treidaajat (2 päivän välein)
    parser_potential = subparsers.add_parser("potential_trades_checker", help="Suorita potentiaalisten treidaajien tarkistus")
    parser_potential.set_defaults(func=run_potential_trades_checker)

    # Tuetut symbolit (30 min välein)
    parser_supported = subparsers.add_parser("supported_symbols_data_fetcher", help="Hae tuettujen symbolien data")
    parser_supported.set_defaults(func=run_supported_symbols_data_fetcher)

    # Pääsymbolien data (5 min välein)
    parser_main = subparsers.add_parser("main_symbols_data_fetcher", help="Hae pääsymbolien data")
    parser_main.set_defaults(func=run_main_symbols_data_fetcher)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func()

if __name__ == "__main__":
    main()
