# modules/symbol_data_fetcher/analysis_summary.py

import json
from datetime import datetime, timedelta
from pathlib import Path

from modules.symbol_data_fetcher.config_symbol_data_fetcher import (
    SYMBOL_LOG_PATH,
    OHLCV_LOG_PATH,
    MAIN_SYMBOLS,
    TOP_N_LONG,
    TOP_N_SHORT,
    LOCAL_TIMEZONE,
    ANALYSIS_MIN_INTERVAL_HOURS,
    TOP_N_EXTRA_TIES,
)
from modules.symbol_data_fetcher.utils import score_asset


def save_analysis_log(symbol_scores):
    now = datetime.now(LOCAL_TIMEZONE)
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # ⚠️ Skip if log already exists within the last ANALYSIS_MIN_INTERVAL_HOURS
    if SYMBOL_LOG_PATH.exists():
        try:
            with open(SYMBOL_LOG_PATH, "r") as f:
                for line in reversed(list(f)):
                    try:
                        existing = json.loads(line)
                        timestamp_str = existing.get("timestamp")
                        if timestamp_str:
                            existing_time = datetime.fromisoformat(timestamp_str).astimezone(LOCAL_TIMEZONE)
                            if now - existing_time < timedelta(hours=ANALYSIS_MIN_INTERVAL_HOURS):
                                print(f"\n⚠️  Analysis log already exists within {ANALYSIS_MIN_INTERVAL_HOURS} hours, skipping save.")
                                return
                            else:
                                break
                    except (json.JSONDecodeError, ValueError):
                        continue
        except OSError:
            print("\n⚠️  Failed to read log file. Writing a new line.")

    # 🧮 Sort and score
    sorted_symbols = sorted(symbol_scores.items(), key=lambda x: x[1]["score"], reverse=True)

    long_syms = [(s, sc["score"]) for s, sc in sorted_symbols if sc["score"] > 0 and s not in MAIN_SYMBOLS]
    short_syms = sorted(
        [(s, sc["score"]) for s, sc in symbol_scores.items() if sc["score"] < 0 and s not in MAIN_SYMBOLS],
        key=lambda x: x[1]
    )

    # 🥇 Top-N long
    top_long = []
    if TOP_N_LONG > 0:
        top_long = long_syms[:TOP_N_LONG]
        if TOP_N_EXTRA_TIES and len(long_syms) > TOP_N_LONG:
            cutoff_score = long_syms[TOP_N_LONG - 1][1]
            extra = [x for x in long_syms[TOP_N_LONG:] if x[1] == cutoff_score]
            top_long += extra

    # 🥇 Top-N short
    top_short = []
    if TOP_N_SHORT > 0:
        top_short = short_syms[:TOP_N_SHORT]
        if TOP_N_EXTRA_TIES and len(short_syms) > TOP_N_SHORT:
            cutoff_score = short_syms[TOP_N_SHORT - 1][1]
            extra = [x for x in short_syms[TOP_N_SHORT:] if x[1] == cutoff_score]
            top_short += extra

    result = {
        "timestamp": now.isoformat(),
        "potential_both_ways": MAIN_SYMBOLS,
        "potential_to_long": [s for s, _ in top_long],
        "potential_to_short": [s for s, _ in top_short],
    }

    with open(SYMBOL_LOG_PATH, "a") as f:
        json.dump(result, f)
        f.write("\n")

    print(f"\n📝 Analysis log saved: {SYMBOL_LOG_PATH}")


def analyze_all_symbols():
    """
    Reads logs and analyzes them.
    Returns sorted long and short lists along with explanations.
    """
    if not OHLCV_LOG_PATH.exists():
        print("❌ OHLCV_LOG_PATH not found.")
        return

    today = datetime.now(LOCAL_TIMEZONE).date()
    yesterday = today - timedelta(days=1)
    symbol_scores = {}

    with open(OHLCV_LOG_PATH, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                ts_str = entry.get("timestamp", "")
                if not (ts_str.startswith(today.isoformat()) or ts_str.startswith(yesterday.isoformat())):
                    continue

                symbol = entry.get("symbol")
                data_preview = entry.get("data_preview")
                timestamp_str = entry.get("timestamp")

                if not (symbol and data_preview and timestamp_str):
                    continue

                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if timestamp.tzinfo is None:
                        timestamp = timestamp.replace(tzinfo=LOCAL_TIMEZONE)
                    timestamp = timestamp.astimezone(LOCAL_TIMEZONE)
                except ValueError:
                    continue

                existing = symbol_scores.get(symbol)
                if existing is None or timestamp > existing["timestamp"]:
                    score = score_asset(data_preview)
                    symbol_scores[symbol] = {
                        "score": score,
                        "timestamp": timestamp,
                    }

            except json.JSONDecodeError:
                continue

    sorted_symbols = sorted(symbol_scores.items(), key=lambda x: x[1]["score"], reverse=True)

    long_symbols = [s for s, data in sorted_symbols if data["score"] > 0 and s not in MAIN_SYMBOLS]
    short_symbols = sorted(
        [s for s, data in symbol_scores.items() if data["score"] < 0 and s not in MAIN_SYMBOLS],
        key=lambda s: symbol_scores[s]["score"]
    )
    print(f"Long symbols: {long_symbols}")
    print(f"Short symbols: {short_symbols}")

    return long_symbols, short_symbols, symbol_scores
