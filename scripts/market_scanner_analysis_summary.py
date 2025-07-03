# AI-crypto-trader/scripts/market_scanner_analysis_summary.py

import json
from datetime import datetime
from pathlib import Path
from configs.market_scanner_config import LOG_PATH, INTERVALS

def score_asset(data_preview):
    """
    Palauttaa pisteet, jossa positiivinen = long bias, negatiivinen = short bias.
    Perustuu RSI- ja MACD-arvoihin usealla aikavälillä.
    """
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

        if rsi is not None:
            if rsi > 70:
                score -= 1 * weight_map[interval]  # yliostettu
            elif rsi < 30:
                score += 1 * weight_map[interval]  # ylimyyty

        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                score += 0.5 * weight_map[interval]
            elif macd < macd_signal:
                score -= 0.5 * weight_map[interval]

    return score


def analyze_all_symbols():
    """
    Lukee logit ja analysoi ne.
    Palauttaa järjestetyt long- ja short-listat sekä selitykset.
    """
    if not LOG_PATH.exists():
        print("❌ LOG_PATH not found.")
        return

    today_str = datetime.utcnow().date().isoformat()
    symbol_scores = {}

    with open(LOG_PATH, "r") as f:
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

    return long_symbols, short_symbols, symbol_scores
