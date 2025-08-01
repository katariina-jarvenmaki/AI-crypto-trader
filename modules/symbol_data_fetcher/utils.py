import math
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from utils.get_timestamp import get_timestamp 
from utils.load_latest_entry import load_latest_entry

def score_asset(data_preview, module_config):
    score = 0
    weight_map = module_config["interval_weights"]
    scoring_params = module_config.get("scoring_parameters", {})

    for interval, interval_weight in weight_map.items():
        d = data_preview.get(interval)
        if not d:
            continue

        # --- RSI ---
        if scoring_params.get("rsi", {}).get("enabled", True):
            rsi = d.get("rsi")
            rsi_cfg = scoring_params.get("rsi", {})
            rsi_weight = rsi_cfg.get("weight", 1.0)
            rsi_upper = rsi_cfg.get("upper", 70)
            rsi_lower = rsi_cfg.get("lower", 30)

            if rsi is not None and not math.isnan(rsi):
                if rsi > rsi_upper:
                    score -= rsi_weight * interval_weight
                elif rsi < rsi_lower:
                    score += rsi_weight * interval_weight

        # --- MACD ---
        if scoring_params.get("macd", {}).get("enabled", True):
            macd = d.get("macd")
            macd_signal = d.get("macd_signal")
            macd_weight = scoring_params.get("macd", {}).get("weight", 0.5)

            if macd is not None and macd_signal is not None:
                if not math.isnan(macd) and not math.isnan(macd_signal):
                    if macd > macd_signal:
                        score += macd_weight * interval_weight
                    elif macd < macd_signal:
                        score -= macd_weight * interval_weight

        # --- Esimerkki: STOCH (laajennus) ---
        if scoring_params.get("stoch", {}).get("enabled", False):
            stoch = d.get("stoch")
            stoch_cfg = scoring_params["stoch"]
            stoch_weight = stoch_cfg.get("weight", 0.7)
            stoch_upper = stoch_cfg.get("overbought", 80)
            stoch_lower = stoch_cfg.get("oversold", 20)

            if stoch is not None and not math.isnan(stoch):
                if stoch > stoch_upper:
                    score -= stoch_weight * interval_weight
                elif stoch < stoch_lower:
                    score += stoch_weight * interval_weight

    return score
