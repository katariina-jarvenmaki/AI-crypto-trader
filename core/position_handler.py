from modules.positions_data_fetcher import positions_data_fetcher

def run_position_handler(current_equity, allowed_negative_margins):

    # Get current ByBit positions
    bybit_positions = positions_data_fetcher.position_data_fetcher()






    print(f"💰 Current equity: {current_equity}")
    print(f"💰 Allowed negative margin threshold: {allowed_negative_margins}")

    print(f"1. Equity checks")
    print(f"2. Position checks: Negative positions count")
    print(f"3. Order limits: Negative positions count")
    print(f"4. Order amount: min_inv_diff_percent")
    print(f"5. After trailing stop loss: Rise leverage")
    print(f"6. Negative margin setting to 25%")