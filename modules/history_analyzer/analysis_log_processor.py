
import os
import json
from modules.history_analyzer.config_history_analyzer import CONFIG

# Tee näistä globaaleja, jotta kaikki funktiot voivat käyttää
priority_keys = [
    "timestamp", "symbol", 
    "price", "price_change", "price_change_percent",
    "avg_rsi", "rsi_change", "rsi_change_percent",
    "ema_rsi", "ema_rsi_change", "ema_rsi_change_percent",
    "macd_diff", "macd_diff_change", "macd_diff_change_percent",
    "macd_trend", "bollinger_status", "ema_trend", "signal_strength", "flag",
    "turnover_status", "rsi_divergence", "rsi_delta",
    "change_24h", "high_price", "low_price", "volume", "turnover",
    "rsi", "ema", "macd", "macd_signal", "bb_upper", "bb_lower",
]

rename_map = {
    "avg_rsi": "avg_rsi_all"
}

def process_log_entry(entry: dict):

    filepath = CONFIG["analysis_log_path"]

    # Luo uusi sanakirja prioriteettiavaimista, mukaan lukien uudelleennimeämiset
    updated_entry = {
        key: entry.get(rename_map.get(key, key)) for key in priority_keys
    }

    save_log(updated_entry, filepath)

def save_log(entry, log_file):
    # Create a new dictionary with fields in desired order
    ordered_entry = {}

    for key in priority_keys:
        if key in entry:
            ordered_entry[key] = entry[key]

    # Add any remaining fields not in priority list
    for key in entry:
        if key not in ordered_entry:
            ordered_entry[key] = entry[key]

    # Create directory if needed
    if os.path.dirname(log_file):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create file if it doesn't exist
    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            pass  # Create empty file

    # Append the entry as a JSON line
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(ordered_entry, ensure_ascii=False) + "\n")

def analysis_log_processor(parsed_entries, analysis_results):

    analysis_dict = {entry['symbol']: entry for entry in analysis_results}

    for entry in parsed_entries:
        symbol = entry.get('symbol')
        analysis_data = analysis_dict.get(symbol)

        if analysis_data:
            merged_entry = {**entry, **analysis_data}
            process_log_entry(merged_entry)

