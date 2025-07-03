# scripts/market_scanner_analysis_summary.py

import json
from datetime import datetime
from pathlib import Path
from configs.market_scanner_config import LOG_PATH, INTERVALS

def save_analysis_log(symbol_scores):
    today_str = datetime.utcnow().date().isoformat()
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    log_path = logs_dir / "market_scanner_analysis_summary.jsonl"

    # 🧪 Tarkistetaan, onko tämän päivän logimerkintä jo olemassa
    if log_path.exists():
        try:
            with open(log_path, "r") as f:
                for line in f:
                    try:
                        existing = json.loads(line)
                        if existing.get("date") == today_str:
                            print(f"\n⚠️  Analyysiloki löytyy jo päivältä {today_str}, ohitetaan tallennus.")
                            return
                    except json.JSONDecodeError:
                        continue
        except OSError:
            print("\n⚠️  Lokitiedoston lukeminen epäonnistui. Kirjoitetaan uusi rivi.")

    # 🧮 Scorojen järjestäminen ja TOP-20 valinta
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

    # 📦 Tallennettava data
    result = {
        "date": today_str,
        "potential_to_long": [s for s, _ in top20_long],
        "potential_to_short": [s for s, _ in top20_short],
    }

    # 💾 Kirjoitus JSONL-tiedostoon (rivi per päivä)
    with open(log_path, "a") as f:
        json.dump(result, f)
        f.write("\n")

    print(f"\n📝 Analyysiloki tallennettu: {log_path}")

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