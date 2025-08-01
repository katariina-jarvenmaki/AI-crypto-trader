import math
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from utils.get_timestamp import get_timestamp 
from utils.load_latest_entry import load_latest_entry

def get_latest_entry(symbol, file_path, max_age_minutes=60):
    try:
        end_time = get_timestamp()
        start_time = (date_parser.isoparse(end_time) - timedelta(minutes=max_age_minutes)).isoformat()

        entries = load_latest_entry(
            file_path=file_path,
            limit=1,
            use_timestamp=True,
            symbols=[symbol],
            start_time=start_time,
            end_time=end_time,
        )

        if not entries:
            return {}

        return entries[0]

    except Exception as e:
        print(f"Error in get_latest_entry: {e}")
        return {}

def score_asset(data_preview, module_config):

    score = 0
    weight_map = module_config['interval_weights']

    for interval in weight_map:
        d = data_preview.get(interval)
        if not d:
            continue

        rsi = d.get("rsi")
        macd = d.get("macd")
        macd_signal = d.get("macd_signal")

        if rsi is not None and not math.isnan(rsi):
            if rsi > 70:
                score -= 1 * weight_map[interval]
            elif rsi < 30:
                score += 1 * weight_map[interval]

        if (macd is not None and not math.isnan(macd)) and (macd_signal is not None and not math.isnan(macd_signal)):
            if macd > macd_signal:
                score += 0.5 * weight_map[interval]
            elif macd < macd_signal:
                score -= 0.5 * weight_map[interval]

    return score