# main.py
import time
import pytz
import pandas as pd
from configs.config import TIMEZONE
from scripts.args_parser import parse_arguments
from runner import run_analysis_for_symbol

def main():

    try:
        selected_platform, selected_symbols, override_signal = parse_arguments()
        
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    while True:
        now = pd.Timestamp.utcnow().replace(tzinfo=pytz.utc).astimezone(TIMEZONE)
        print(f"\n🕒 Starting signal analysis loop {now:%Y-%m-%d %H:%M:%S %Z}")
        print(f"✅ Selected platform: {selected_platform}")
        print(f"✅ Selected symbols: {selected_symbols}")

        for i, symbol in enumerate(selected_symbols):
            run_analysis_for_symbol(symbol, override_signal if i == 0 else None)

        print("🕒 Sleeping for 5 minutes...\n")
        time.sleep(300)

if __name__ == "__main__":
    main()
