import pytz
from datetime import datetime
from configs.config import TIMEZONE

def collect_analysis_summary(position_counts, calculated_margins, available_margins):

    timestamp = datetime.now(TIMEZONE).isoformat()

    summary = {
        "timestamp": timestamp,
        "position_counts": position_counts,
        "calculated_margins": calculated_margins,
        "available_margins": available_margins
    }

    return summary
    
def count_positions(positions, verbose=True):
    total_shorts = 0
    total_longs = 0
    shorts_without_trailing_stop = 0
    longs_without_trailing_stop = 0

    for position in positions:
        side = position.get("side")
        trailing_stop = position.get("trailingStop")

        if side == "Sell":
            total_shorts += 1
            if trailing_stop == "0":
                shorts_without_trailing_stop += 1
        elif side == "Buy":
            total_longs += 1
            if trailing_stop == "0":
                longs_without_trailing_stop += 1

    if verbose:
        print("\n=== Trade counts ===")
        print(f"Total shorts: {total_shorts}")
        print(f"Total longs: {total_longs}")
        print(f"Shorts without trailing stop: {shorts_without_trailing_stop}")
        print(f"Longs without trailing stop: {longs_without_trailing_stop}")

    return {
        "total_shorts": total_shorts,
        "total_longs": total_longs,
        "shorts_without_trailing_stop": shorts_without_trailing_stop,
        "longs_without_trailing_stop": longs_without_trailing_stop,
    }

def calculate_margin_without_trailing_stop(positions, verbose=True):
    shorts_margin = 0.0
    longs_margin = 0.0

    for position in positions:
        side = position.get("side")
        trailing_stop = position.get("trailingStop")
        margin = float(position.get("positionBalance", 0))

        if trailing_stop == "0":
            if side == "Sell":
                shorts_margin += margin
            elif side == "Buy":
                longs_margin += margin

    if verbose:
        print("\n=== Margin without trailing stop ===")
        print(f"Total margin used by shorts without trailing stop: {shorts_margin:.4f}")
        print(f"Total margin used by longs without trailing stop: {longs_margin:.4f}")

    return {
        "shorts_margin": shorts_margin,
        "longs_margin": longs_margin,
    }

def calculate_available_margins(calculated_margin, allowed_negative_margins, verbose=True):
    longs_margin = calculated_margin.get('longs_margin', 0.0)
    shorts_margin = calculated_margin.get('shorts_margin', 0.0)

    allowed_long = allowed_negative_margins.get('long', 0.0)
    allowed_short = allowed_negative_margins.get('short', 0.0)

    long_diff = allowed_long - longs_margin
    short_diff = allowed_short - shorts_margin

    available_long_margin = long_diff if long_diff > 0 else 0.0
    available_short_margin = short_diff if short_diff > 0 else 0.0

    if verbose:
        print("\n=== Available margin for trades ===")
        print(f"Available long margin: {available_long_margin:.4f}")
        print(f"Available short margin: {available_short_margin:.4f}")
    
    return {
        'available_long_margin': available_long_margin,
        'available_short_margin': available_short_margin
    }

def positions_analyzer(positions, allowed_negative_margins, verbose=True):
    if not positions:
        if verbose:
            print("No open positions.")
        return

    if verbose:
        print("\nAnalyzing the positions...")

    position_counts = count_positions(positions, verbose)
    calculated_margins = calculate_margin_without_trailing_stop(positions, verbose)
    available_margins = calculate_available_margins(calculated_margins, allowed_negative_margins, verbose)

    analysis_summary = collect_analysis_summary(position_counts, calculated_margins, available_margins)

    if verbose:
        print("\n=== Analysis Summary ===")
        print(analysis_summary)

    return analysis_summary

if __name__ == "__main__":

    from modules.positions_data_fetcher import positions_data_fetcher

    allowed_negative_margins = 53.0
    positions = positions_data_fetcher.position_data_fetcher()
    positions_analyzer(positions, allowed_negative_margins)
