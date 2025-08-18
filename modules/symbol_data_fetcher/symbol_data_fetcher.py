# modules/symbol_data_fetcher/symbol_data_fetcher.py
# version 2.0, aug 2025

import argparse
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from modules.symbol_data_fetcher.tasks.potential_trades_checker import run_potential_trades_checker
from modules.symbol_data_fetcher.tasks.fetch_symbols_data import run_fetch_symbols_data

from utils.load_latest_entry import load_latest_entry
from utils.load_configs_and_logs import load_configs_and_logs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def conf_and_paths():

    configs_and_logs = load_configs_and_logs([
        {
            "name": "symbol",
            "mid_folder": "analysis",
            "module_key": "symbol_data_fetcher",
            "extension": ".jsonl",
            "return": ["config", "logs_path", "full_log_path", "full_log_schema_path"]
        },
        {
            "name": "ohlcv",
            "mid_folder": "fetch",
            "module_key": "multi_interval_ohlcv",
            "extension": ".jsonl",
            "return": ["full_log_path", "full_log_schema_path"]
        }
    ])

    general_config = configs_and_logs.get("general_config")
    symbol_config = configs_and_logs.get("symbol_config")
    symbol_logs_path = configs_and_logs.get("symbol_logs_path")
    symbol_full_log_path = configs_and_logs.get("symbol_full_log_path")
    symbol_full_log_schema_path = configs_and_logs.get("symbol_full_log_schema_path")
    ohlcv_full_log_path = configs_and_logs.get("ohlcv_full_log_path")
    ohlcv_full_log_schema_path = configs_and_logs.get("ohlcv_full_log_schema_path")
    
    return {
        "general_config": general_config,
        "module_config": symbol_config,
        "module_logs_path": symbol_logs_path,
        "module_log_path": symbol_full_log_path,
        "module_schema_path": symbol_full_log_schema_path,
        "ohlcv_log_path": ohlcv_full_log_path,
        "ohlcv_schema_path": ohlcv_full_log_schema_path,
    }

def symbol_data_fetcher():
    parser = argparse.ArgumentParser(
        description="Symbol Data Fetcher - executes various background tasks for market data analysis."
    )
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available tasks"
    )

    # Lisää alikomennot
    subparsers.add_parser("potential_trades_checker", help="Run potential traders check")
    subparsers.add_parser("fetch_symbols_data", help="Fetch symbols data")

    args = parser.parse_args()
    conf = conf_and_paths()

    if args.command == "potential_trades_checker":
        run_potential_trades_checker(
            conf["general_config"],
            conf["module_config"],
            conf["module_logs_path"],
            conf["module_log_path"],
            conf["module_schema_path"]
        )

    elif args.command == "fetch_symbols_data":
        run_fetch_symbols_data(
            conf["general_config"],
            conf["module_config"],
            conf["module_logs_path"],
            conf["module_schema_path"],
            conf["ohlcv_log_path"],
            conf["ohlcv_schema_path"]
        )

    elif args.command is None:
        logging.info("No command given. Running both: potential_trades_checker -> fetch_symbols_data")
        run_potential_trades_checker(
            conf["general_config"],
            conf["module_config"],
            conf["module_logs_path"],
            conf["module_log_path"],
            conf["module_schema_path"]
        )
        run_fetch_symbols_data(
            conf["general_config"],
            conf["module_config"],
            conf["module_log_path"],
            conf["module_schema_path"],
            conf["ohlcv_log_path"],
            conf["ohlcv_schema_path"]
        )

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    symbol_data_fetcher()
