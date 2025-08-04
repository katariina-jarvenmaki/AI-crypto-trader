# main.py

import time
import pytz
import pandas as pd

from configs.config import TIMEZONE
from core.args_parser import parse_arguments
from scripts.log_cleaner import run_log_cleanup
from core.position_handler import run_position_handler
from scripts.order_limiter import load_initiated_orders
from utils.get_symbols_to_use import get_symbols_to_use
from modules.pathbuilder.pathbuilder import pathbuilder
from modules.equity_manager.equity_manager import run_equity_manager
from modules.load_and_validate.load_and_validate import load_and_validate
from core.runner import run_analysis_for_symbol, check_positions_and_update_logs, stop_loss_checker, leverage_updater_for_positive_trades
from modules.equity_manager.equity_stoploss_updater import update_equity_stoploss
from global_state import POSITIONS_RESULT 

def main():

    try:
        selected_platform, selected_symbols, override_signal, trade_mode = parse_arguments()
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    # Set default flags based on trade_mode
    if trade_mode == "long-only":
        long_only_flag = True
        short_only_flag = False
    elif trade_mode == "short-only":
        long_only_flag = False
        short_only_flag = True
    elif trade_mode == "no-trade":
        long_only_flag = False
        short_only_flag = False
    else:
        long_only_flag = False
        short_only_flag = False

    general_config = load_and_validate()
    paths = pathbuilder(
        extension=".jsonl",
        file_name=general_config["module_filenames"]["symbol_data_fetcher"],
        mid_folder="analysis"
    )

    module_config = load_and_validate(
        file_path=paths["full_config_path"],
        schema_path=paths["full_config_schema_path"]
    )

    # ✅ Define module_log_path here
    module_log_path = paths["full_log_path"]

    # Then use it
    if(long_only_flag == True):
        symbol_mode = "long-only"
    elif(short_only_flag == True):
        symbol_mode = "short-only"
    else:
        symbol_mode = None
    result = get_symbols_to_use(module_config, module_log_path, symbol_mode)
    selected_symbols = list(result["symbols_to_trade"])
    
    # Clean the logs
    run_log_cleanup()

    global_is_first_run = True
    equity_stoploss_updated = False 

    while True:

        # Make a equity safety check
        equity_result, status = run_equity_manager()
        if equity_result.get("block_trades", False):
            if not equity_stoploss_updated:
                update_equity_stoploss(
                    equity_stoploss_margin=equity_result.get("equity_stoploss_margin"),
                )
                equity_stoploss_updated = True
            print(f"\n🕒 Waiting for next Equity check...\n")
            time.sleep(300)
            continue
        else:
            print(f"\n✅ Equity check passed! All fine!\n")
            equity_stoploss_updated = False
            
        current_equity = equity_result.get("current_equity")
        minimum_investment = equity_result.get("minimum_investment")
        min_inv_diff_percent = equity_result.get("min_inv_diff_percent")
        allowed_negative_margins = equity_result.get("allowed_negative_margins")

        # Position handler to update and analyse positions
        positions_result = run_position_handler(current_equity, allowed_negative_margins)
        import global_state
        global_state.POSITIONS_RESULT = positions_result

        print(f"💰 Current equity: {current_equity}")
        print(f"💰 Allowed negative margin threshold: {allowed_negative_margins}")

        print(f"1. Equity checks...")
        print(f"2. Position checks: Negative positions count & Available margin calculation")
        print(f"3. Order limits: Negative positions count")
        print(f"4. Order amount: min_inv_diff_percent")
        print(f"5. After trailing stop loss: Rise leverage")
        print(f"6. Negative margin setting to 25%")

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

            long_only_flag = False
            short_only_flag = False

            if trade_mode == "long_only":
                long_only_flag = True
                short_only_flag = False
            elif trade_mode == "short_only":
                long_only_flag = False
                short_only_flag = True
            elif trade_mode == "no_trade":
                long_only_flag = False
                short_only_flag = False
            else:
                long_only_flag = mode.get("long_only", False)
                short_only_flag = mode.get("short_only", False)

            run_analysis_for_symbol(
                selected_symbols=selected_symbols,
                symbol=symbol,
                is_first_run=global_is_first_run,
                override_signal=current_override_signal,
                long_only=long_only_flag,
                short_only=short_only_flag,
                initiated_counts=initiated_counts,
                min_inv_diff_percent = min_inv_diff_percent,
                no_trade = (trade_mode == "no_trade")
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

        leverage_updater_for_positive_trades()

        print("\n🕒 Sleeping to next round...")
        time.sleep(180)

if __name__ == "__main__":
    main()