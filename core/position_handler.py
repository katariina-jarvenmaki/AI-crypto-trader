from modules.positions_data_fetcher import positions_data_fetcher
from modules.positions_analyzer.positions_analyzer import positions_analyzer

def run_position_handler(current_equity, allowed_negative_margins):

    # Get current ByBit positions
    bybit_positions = positions_data_fetcher.position_data_fetcher()

    # Call analyzer silently
    position_analyses = positions_analyzer(bybit_positions, allowed_negative_margins, verbose=False)

    # Return analysis data
    return position_analyses 
