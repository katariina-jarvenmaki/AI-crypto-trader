# modules/symbol_data_fetcher/utils.py

from pathlib import Path

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

def prepare_temporary_log(log_name: str = "temp_log.jsonl") -> Path:

    """Luo tai tyhjentää lokaalin log-tiedoston samassa kansiossa kuin tämä tiedosto."""

    current_dir = Path(__file__).parent  # Sama kansio missä tämä tiedosto sijaitsee
    log_file = current_dir / log_name

    log_file.write_text("")  # Tyhjennä tiedosto (luo sen jos ei ole)

    return log_file
