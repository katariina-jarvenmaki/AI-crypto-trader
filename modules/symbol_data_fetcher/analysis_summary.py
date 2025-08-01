# modules/symbol_data_fetcher/analysis_summary.py
# version 2.0, aug 2025

from datetime import datetime, timedelta
from utils.get_timestamp import get_timestamp 
from modules.symbol_data_fetcher.utils import score_asset

def prepare_analysis_results(symbol_scores, module_config):

    now = datetime.fromisoformat(get_timestamp())

    # 🧮 Lajitellaan skoret
    sorted_symbols = sorted(symbol_scores.items(), key=lambda x: x[1]["score"], reverse=True)

    min_score_long = module_config.get("score_filter_threshold_long", 0)
    min_score_short = module_config.get("score_filter_threshold_short", 0)

    long_syms = [(s, sc["score"]) for s, sc in sorted_symbols if sc["score"] > min_score_long and s not in module_config["main_symbols"]]
    short_syms = sorted(
        [(s, sc["score"]) for s, sc in symbol_scores.items() if sc["score"] < min_score_short and s not in module_config["main_symbols"]],
        key=lambda x: x[1]
    )

    # 🥇 Top-N long
    top_long = []
    if module_config["top_n_long"]> 0:
        top_long = long_syms[:module_config["top_n_long"]]
        if module_config["top_n_extra_ties"] and len(long_syms) > module_config["top_n_long"]:
            cutoff_score = long_syms[module_config["top_n_long"]- 1][1]
            extra = [x for x in long_syms[module_config["top_n_long"]:] if x[1] == cutoff_score]
            top_long += extra

    # 🥇 Top-N short
    top_short = []
    if module_config["top_n_short"] > 0:
        top_short = short_syms[:module_config["top_n_short"]]
        if module_config["top_n_extra_ties"] and len(short_syms) > module_config["top_n_short"]:
            cutoff_score = short_syms[module_config["top_n_short"] - 1][1]
            extra = [x for x in short_syms[module_config["top_n_short"]:] if x[1] == cutoff_score]
            top_short += extra

    # 📦 Lopullinen tulos
    result = {
        "timestamp": now.isoformat(),
        "potential_both_ways": module_config["main_symbols"],
        "potential_to_long": [s for s, _ in top_long],
        "potential_to_short": [s for s, _ in top_short],
    }

    return [result]

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

            include_days_back = module_config.get("analysis_include_days_back", 1)
            valid_dates = {today - timedelta(days=i) for i in range(include_days_back + 1)}

            if timestamp.date() not in valid_dates:
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