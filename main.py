# main.py

import time
import pytz
import pandas as pd
from configs.config import TIMEZONE
from core.args_parser import parse_arguments
from core.runner import run_analysis_for_symbol, check_positions_and_update_logs, stop_loss_checker
from scripts.log_cleaner import run_log_cleanup
from scripts.order_limiter import load_initiated_orders

def main():

    # Suoritetaan logien siivous ennen sovelluksen ajoa
    run_log_cleanup()

    try:
        selected_platform, selected_symbols, override_signal, long_only, short_only = parse_arguments()

    except ValueError as e:
        print(f"[ERROR] {e}")
        return
    
    global_is_first_run = True 
    
    # Start a turn
    while True:

        now = pd.Timestamp.utcnow().replace(tzinfo=pytz.utc).astimezone(TIMEZONE)
        print("\n-----------------------------------------------------------------")
        print(f"🕒 Starting signal analysis loop {now:%Y-%m-%d %H:%M:%S %Z}")
        print(f"✅ Selected platform: {selected_platform}")
        print(f"✅ Selected symbols: {selected_symbols}")
        print("-----------------------------------------------------------------")

        for i, symbol in enumerate(selected_symbols):

            current_override_signal = None
            if global_is_first_run and i == 0:
                current_override_signal = override_signal 

            initiated_counts = load_initiated_orders()

            run_analysis_for_symbol(
                selected_symbols=selected_symbols,
                symbol=symbol,
                is_first_run=global_is_first_run,
                override_signal=current_override_signal,
                long_only=long_only,
                short_only=short_only,
                initiated_counts=initiated_counts
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