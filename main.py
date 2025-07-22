# main.py

import time
import pytz
import pandas as pd
import json

from pathlib import Path
from configs.config import TIMEZONE
from core.args_parser import parse_arguments
from core.runner import run_analysis_for_symbol, check_positions_and_update_logs, stop_loss_checker
from scripts.log_cleaner import run_log_cleanup
from scripts.order_limiter import load_initiated_orders
from modules.equity_manager.equity_manager import run_equity_manager

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

def main():

    run_log_cleanup()

    try:
        selected_platform, selected_symbols, override_signal, long_only_flag, short_only_flag = parse_arguments()
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    try:
        symbol_modes = load_symbol_modes(selected_symbols, long_only_flag, short_only_flag)
    except Exception as e:
        print(f"[ERROR] Failed to load symbol modes: {e}")
        return

    global_is_first_run = True
    
    while True:
        equity_result = run_equity_manager()
        if equity_result.get("block_trades", False):
            time.sleep(300)
            continue
        allowed_negative_margins = equity_result.get("allowed_negative_margins")

        now = pd.Timestamp.utcnow().replace(tzinfo=pytz.utc).astimezone(TIMEZONE)
        print("\n-----------------------------------------------------------------")
        print(f"🕒 Starting signal analysis loop {now:%Y-%m-%d %H:%M:%S %Z}")
        print(f"✅ Selected platform: {selected_platform}")
        print(f"✅ Selected symbols: {selected_symbols}")
        print("-----------------------------------------------------------------")

        for i, symbol in enumerate(selected_symbols):
            current_override_signal = override_signal if global_is_first_run and i == 0 else None
            initiated_counts = load_initiated_orders()

            mode = symbol_modes.get(symbol, {"long_only": False, "short_only": False})

            run_analysis_for_symbol(
                selected_symbols=selected_symbols,
                symbol=symbol,
                is_first_run=global_is_first_run,
                override_signal=current_override_signal,
                long_only=mode["long_only"],
                short_only=mode["short_only"],
                initiated_counts=initiated_counts,
                allowed_negative_margins=allowed_negative_margins 
            )

        global_is_first_run = False 

        positions = check_positions_and_update_logs(
            symbols_to_check=selected_symbols,
            platform="ByBit"
        )
        if positions:
            print("🟢 Open positions found from ByBit:")
            for p in positions:
                print(f"🔸 {p['symbol']}: {p['side']} | Size: {p['size']}")
        else:
            print("⚪ No open positions found.")
            time.sleep(180)
            continue

        stop_loss_checker(positions)

        print("\n🕒 Sleeping to next round...")
        time.sleep(180)

if __name__ == "__main__":
    main()