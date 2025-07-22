from modules.positions_data_fetcher import positions_data_fetcher
from modules.positions_analyzer.positions_analyzer import positions_analyzer

def run_position_handler(current_equity, allowed_negative_margins):

    # Get current ByBit positions
    bybit_positions = positions_data_fetcher.position_data_fetcher()

    # Call analyzer silently
    position_analyses = positions_analyzer(bybit_positions, allowed_negative_margins, verbose=False)
    print(f"Position analyses: {position_analyses}")

    print(f"💰 Current equity: {current_equity}")
    print(f"💰 Allowed negative margin threshold: {allowed_negative_margins}")

    print(f"1. Equity checks...")
    print(f"2. Position checks: Negative positions count & Available margin calculation")
    print(f"3. Order limits: Negative positions count")
    print(f"4. Order amount: min_inv_diff_percent")
    print(f"5. After trailing stop loss: Rise leverage")
    print(f"6. Negative margin setting to 25%")
