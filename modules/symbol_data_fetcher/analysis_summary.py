# modules/symbol_data_fetcher/analysis_summary.py

import json
from datetime import datetime, timedelta
from pathlib import Path

from modules.symbol_data_fetcher.symbol_data_fetcher_config import (
    SYMBOL_LOG_PATH,
    OHLCV_LOG_PATH,
    MAIN_SYMBOLS,
    TOP_N_LONG,
    TOP_N_SHORT,
    LOCAL_TIMEZONE,
)
from modules.symbol_data_fetcher.utils import score_asset

def save_analysis_log(symbol_scores):
    now = datetime.now(LOCAL_TIMEZONE)
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # ⚠️ Skip if log already exists within the last 3 hours
    if SYMBOL_LOG_PATH.exists():
        try:
            with open(SYMBOL_LOG_PATH, "r") as f:
                for line in reversed(list(f)):  # Iterate the log from end to start
                    try:
                        existing = json.loads(line)
                        timestamp_str = existing.get("timestamp")
                        if timestamp_str:
                            existing_time = datetime.fromisoformat(timestamp_str).astimezone(LOCAL_TIMEZONE)
                            if now - existing_time < timedelta(hours=3):
                                print(f"\n⚠️  Analysis log already exists within 3 hours, skipping save.")
                                return
                            else:
                                break  # No need to check older entries
                    except (json.JSONDecodeError, ValueError):
                        continue
        except OSError:
            print("\n⚠️  Failed to read log file. Writing a new line.")

    # 🧮 Sort and score
    sorted_symbols = sorted(symbol_scores.items(), key=lambda x: x[1]["score"], reverse=True)

    # ⚖️ Filter only positive and negative — score == 0 is removed
    long_syms = [(s, sc["score"]) for s, sc in sorted_symbols if sc["score"] > 0]
    short_syms = sorted(
        [(s, sc["score"]) for s, sc in symbol_scores.items() if sc["score"] < 0],
        key=lambda x: x[1]
    )
    
    # 🥇 Top-20 long
    top20_long = long_syms[:TOP_N_LONG]
    if len(long_syms) > TOP_N_LONG:
        last_score = top20_long[-1][1]
        top20_long += [x for x in long_syms[TOP_N_LONG:] if x[1] == last_score]

    # 🥇 Top-20 short
    top20_short = short_syms[:TOP_N_SHORT]
    if len(short_syms) > TOP_N_SHORT:
        last_score = top20_short[-1][1]
        top20_short += [x for x in short_syms[TOP_N_SHORT:] if x[1] == last_score]

    # 📦 Save result with timestamp
    result = {
        "timestamp": now.isoformat(),
        "potential_both_ways": MAIN_SYMBOLS,
        "potential_to_long": [s for s, _ in top20_long],
        "potential_to_short": [s for s, _ in top20_short],
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

    long_symbols = [s for s, data in sorted_symbols if data["score"] > 0]
    short_symbols = [s for s, data in sorted_symbols if data["score"] < 0]
    print(f"Long symbols: {long_symbols}")
    print(f"Short symbols: {short_symbols}")

    return long_symbols, short_symbols, symbol_scores
