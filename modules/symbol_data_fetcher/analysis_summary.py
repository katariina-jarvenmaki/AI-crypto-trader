# modules/symbol_data_fetcher/analysis_summary.py
from datetime import datetime, timedelta
from utils.get_timestamp import get_timestamp 
from modules.symbol_data_fetcher.utils import score_asset

def analyze_all_symbols(latest_entries, module_config):
    """
    Analyzes given OHLCV entries.
    Returns sorted long and short lists along with explanations.
    """
    now = datetime.fromisoformat(get_timestamp())
    today = now.date()
    yesterday = today - timedelta(days=1)

    symbol_scores = {}

    for entry in latest_entries.values():
        try:
            ts_str = entry.get("timestamp", "")
            try:
                timestamp = datetime.fromisoformat(ts_str)
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=now.tzinfo)
                timestamp = timestamp.astimezone(now.tzinfo)
            except ValueError:
                continue

            if timestamp.date() not in (today, yesterday):
                continue

            symbol = entry.get("symbol", "").upper()
            if symbol in module_config["blocked_symbols"] or symbol in module_config["main_symbols"]:
                continue

            data_preview = entry.get("data_preview")
            timestamp_str = entry.get("timestamp")
            if not (symbol and data_preview and timestamp_str):
                continue
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=now.tzinfo)
                timestamp = timestamp.astimezone(now.tzinfo)
            except ValueError:
                continue

            existing = symbol_scores.get(symbol)
            if existing is None or timestamp > existing["timestamp"]:
                score = score_asset(data_preview, module_config)
                symbol_scores[symbol] = {
                    "score": score,
                    "timestamp": timestamp,
                }

        except Exception:
            continue

    sorted_symbols = sorted(symbol_scores.items(), key=lambda x: x[1]["score"], reverse=True)

    long_symbols = [s for s, data in sorted_symbols if data["score"] > 0 and s not in module_config["main_symbols"] and s not in module_config["blocked_symbols"]]
    short_symbols = sorted(
        [s for s, data in symbol_scores.items() if data["score"] < 0 and s not in module_config["main_symbols"] and s not in module_config["blocked_symbols"]],
        key=lambda s: symbol_scores[s]["score"]
    )

    print(f"\nLong symbols: {long_symbols}")
    print(f"\nShort symbols: {short_symbols}")

    return long_symbols, short_symbols, symbol_scores