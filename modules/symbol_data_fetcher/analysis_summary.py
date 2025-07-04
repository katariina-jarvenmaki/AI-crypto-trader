# modules/symbol_data_fetcher/analysis_summary.py

import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from modules.symbol_data_fetcher.symbol_data_fetcher_config import SYMBOL_LOG_PATH, OHLCV_LOG_PATH, INTERVALS, MAIN_SYMBOLS, TOP_N_LONG, TOP_N_SHORT, INTERVAL_WEIGHTS, LOCAL_TIMEZONE

def save_analysis_log(symbol_scores):
    now = datetime.now(LOCAL_TIMEZONE)
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # ⚠️ Skip if log already exists within the last 3 hours
    if SYMBOL_LOG_PATH.exists():
        try:
            with open(SYMBOL_LOG_PATH, "r") as f:
                for line in reversed(list(f)):  # Käydään logia läpi lopusta alkuun
                    try:
                        existing = json.loads(line)
                        timestamp_str = existing.get("timestamp")
                        if timestamp_str:
                            existing_time = datetime.fromisoformat(timestamp_str).astimezone(LOCAL_TIMEZONE)
                            if now - existing_time < timedelta(hours=3):
                                print(f"\n⚠️  Analysis log already exists within 3 hours, skipping save.")
                                return
                            else:
                                break  # Ei tarvitse tarkistaa enää vanhempia
                    except (json.JSONDecodeError, ValueError):
                        continue
        except OSError:
            print("\n⚠️  Failed to read log file. Writing a new line.")

    # 🧮 Sort and score
    sorted_symbols = sorted(symbol_scores.items(), key=lambda x: x[1], reverse=True)

    # ⚖️ Suodatetaan vain positiiviset ja negatiiviset — score == 0 poistetaan
    long_syms = [(s, sc) for s, sc in sorted_symbols if sc > 0]
    short_syms = [(s, sc) for s, sc in sorted_symbols if sc < 0]

    # 🥇 Top-20 long
    top20_long = long_syms[:TOP_N_LONG]
    if len(long_syms) > 20:
        last_score = top20_long[-1][1]
        top20_long += [x for x in long_syms[20:] if x[1] == last_score]

    # 🥇 Top-20 short
    top20_short = short_syms[:TOP_N_SHORT]
    if len(short_syms) > 20:
        last_score = top20_short[-1][1]
        top20_short += [x for x in short_syms[20:] if x[1] == last_score]

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

def score_asset(data_preview):
    score = 0
    weight_map = INTERVAL_WEIGHTS

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

def analyze_all_symbols():
    """
    Reads logs and analyzes them.
    Returns sorted long and short lists along with explanations.
    """

    if not OHLCV_LOG_PATH.exists():
        print("❌ OHLCV_LOG_PATH not found.")
        return

    today_str = datetime.now(LOCAL_TIMEZONE).date().isoformat()
    symbol_scores = {}

    with open(OHLCV_LOG_PATH, "r") as f:
        print(f"Opened OHLCV log path")
        for line in f:
            try:
                entry = json.loads(line)
                if not entry.get("timestamp", "").startswith(today_str):
                    continue

                symbol = entry.get("symbol")
                data_preview = entry.get("data_preview")

                if symbol and data_preview:
                    score = score_asset(data_preview)
                    symbol_scores[symbol] = score

            except json.JSONDecodeError:
                continue

    sorted_symbols = sorted(symbol_scores.items(), key=lambda x: x[1], reverse=True)

    long_symbols = [s for s, score in sorted_symbols if score > 0]
    short_symbols = [s for s, score in sorted_symbols if score < 0]
    print(f"Long symbols: {long_symbols}")
    print(f"Short symbols: {short_symbols}")

    return long_symbols, short_symbols, symbol_scores
