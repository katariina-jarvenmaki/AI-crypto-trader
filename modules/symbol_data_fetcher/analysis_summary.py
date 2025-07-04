# modules/symbol_data_fetcher/analysis_summary.py

import json
from datetime import datetime
from pathlib import Path
from modules.symbol_data_fetcher.supported_symbol_config import SYMBOL_LOG_PATH, OHLCV_LOG_PATH, INTERVALS

def save_analysis_log(symbol_scores):

    today_str = datetime.utcnow().date().isoformat()
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # 🧪 Check if today's log entry already exists
    if SYMBOL_LOG_PATH.exists():
        try:
            with open(SYMBOL_LOG_PATH, "r") as f:
                for line in f:
                    try:
                        existing = json.loads(line)
                        if existing.get("date") == today_str:
                            print(f"\n⚠️  Analysis log already exists for {today_str}, skipping save.")
                            return
                    except json.JSONDecodeError:
                        continue
        except OSError:
            print("\n⚠️  Failed to read log file. Writing a new line.")

    # 🧮 Sort scores and select TOP-20
    sorted_symbols = sorted(symbol_scores.items(), key=lambda x: x[1], reverse=True)

    long_syms = [(s, sc) for s, sc in sorted_symbols if sc > 0]
    top20_long = long_syms[:20]
    if len(long_syms) > 20:
        last_score = top20_long[-1][1]
        top20_long += [x for x in long_syms[20:] if x[1] == last_score]

    short_syms = [(s, sc) for s, sc in sorted_symbols if sc < 0]
    top20_short = short_syms[:20]
    if len(short_syms) > 20:
        last_score = top20_short[-1][1]
        top20_short += [x for x in short_syms[20:] if x[1] == last_score]

    # 📦 Data to be saved
    result = {
        "date": today_str,
        "potential_to_long": [s for s, _ in top20_long],
        "potential_to_short": [s for s, _ in top20_short],
    }

    # 💾 Write to JSONL file (one line per day)
    with open(SYMBOL_LOG_PATH, "a") as f:
        json.dump(result, f)
        f.write("\n")

    print(f"\n📝 Analysis log saved: {SYMBOL_LOG_PATH}")

def score_asset(data_preview):
    score = 0
    weight_map = {
        "1h": 1.0,
        "4h": 1.5,
        "1d": 2.0,
    }

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
    print(f"Analyzing the symbols")
    if not OHLCV_LOG_PATH.exists():
        print("❌ OHLCV_LOG_PATH not found.")
        return

    today_str = datetime.utcnow().date().isoformat()
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
                    print(f"Got the data from score_asset")

            except json.JSONDecodeError:
                continue

    sorted_symbols = sorted(symbol_scores.items(), key=lambda x: x[1], reverse=True)

    long_symbols = [s for s, score in sorted_symbols if score > 0]
    short_symbols = [s for s, score in sorted_symbols if score < 0]
    print(f"Long symbols: {long_symbols}")
    print(f"Short symbols: {short_symbols}")

    return long_symbols, short_symbols, symbol_scores
