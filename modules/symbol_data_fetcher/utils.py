# modules/symbol_data_fetcher/utils.py

from pathlib import Path
import time

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

def append_temp_to_ohlcv_log_until_success(temp_path: Path, target_path: Path, max_retries: int = 5, retry_delay: float = 1.0):

    if not temp_path.exists():
        print(f"Temp file {temp_path} does not exist, nothing to append.")
        return

    for attempt in range(1, max_retries + 1):
        try:
            # Lue temp-tiedoston sisältö
            with open(temp_path, "r") as temp_file:
                temp_lines = temp_file.readlines()

            # Lisää temp_lines target_pathin loppuun
            with open(target_path, "a") as target_file:
                target_file.writelines(temp_lines)

            # Tarkistus: luetaan target_path ja varmistetaan, että kaikki temp_lines löytyvät
            with open(target_path, "r") as target_file:
                target_lines = target_file.readlines()

            # Varmistetaan, että temp_lines ovat peräkkäin target_linesin lopussa
            if target_lines[-len(temp_lines):] == temp_lines:
                print(f"Successfully appended temp file contents to {target_path} on attempt {attempt}.")
                break
            else:
                raise IOError("Verification failed: appended lines not found in target file.")

        except Exception as e:
            print(f"Attempt {attempt} failed with error: {e}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached, failed to append temp file.")
                raise
