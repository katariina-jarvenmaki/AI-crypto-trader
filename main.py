# main.py
import time
import pytz
import pandas as pd
from configs.config import TIMEZONE
from core.args_parser import parse_arguments
from core.runner import run_analysis_for_symbol 

def main():

    try:
        selected_platform, selected_symbols, override_signal = parse_arguments() # Tässä se on 'override_signal'
        
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
        
            run_analysis_for_symbol(symbol=symbol, 
                is_first_run=global_is_first_run, 
                override_signal=current_override_signal)

        global_is_first_run = False 

        print("\n🕒 Sleeping for 5 minutes...")
        time.sleep(300)

if __name__ == "__main__":
    main()