# modules/datetime_analyzer/datetime_analyzer.py

import json
import os
from datetime import datetime, timedelta
from configs.config import LOCAL_TIMEZONE

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config_datetime_analyzer.json")
SENTIMENT_LOG_FILE = "../AI-crypto-trader-logs/analysis-data/history_sentiment_log.jsonl"

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        full_config = json.load(file)
        settings = full_config.get("settings", {})
        return full_config, settings

def get_latest_sentiment_state():
    if not os.path.exists(SENTIMENT_LOG_FILE):
        print(f"⚠️ File not found: {SENTIMENT_LOG_FILE}")
        return None
    try:
        with open(SENTIMENT_LOG_FILE, "r", encoding="utf-8") as f:
            last_line = None
            for line in f:
                if line.strip():
                    last_line = line
            if not last_line:
                return None

            data = json.loads(last_line)
            result = data.get("result", {})
            print(f"✅ Found sentiment result: {result}")
            return {
                "broad_state": result.get("broad_state"),
                "last_hour_state": result.get("last_hour_state")
            }
    except json.JSONDecodeError:
        print("⚠️ Invalid JSON in sentiment log.")
    return None

def determine_mode(state):

    if not state:
        return "default"

    broad = state.get("broad_state")
    last_hour = state.get("last_hour_state")

    if broad == "bull" and last_hour == "bull":
        return "bullish"
    elif broad == "bear" and last_hour == "bear":
        return "bearish"
    elif (
        ("neutral" in (broad, last_hour))
        and (broad in ("bull", "bear", "neutral"))
        and (last_hour in ("bull", "bear", "neutral"))
    ):
        return "neutral"
    else:
        return "default"

def get_current_trend_for_now(config_data, weekday, mode, now, lookahead_minutes):
    """Palauttaa nykyhetkeen sopivan trendin, siirtää aikaa lookahead_minutes taaksepäin"""
    day_data = config_data.get(weekday)
    if not day_data:
        return None

    block = day_data.get(mode) or day_data.get("default", [])

    lookahead_time = (now - timedelta(minutes=lookahead_minutes)).time()

    for entry in block:
        if not isinstance(entry, dict):
            continue
        start_str, end_str = entry["time"].split("-")
        start = datetime.strptime(start_str.strip(), "%H:%M").time()
        end = datetime.strptime(end_str.strip(), "%H:%M").time()

        if start <= end:
            if start <= lookahead_time < end:
                return entry["trend"]
        else:
            if lookahead_time >= start or lookahead_time < end:
                return entry["trend"]
    return None

def get_preferences(config_data, weekday, now, sentiment_state, settings):
    mode = determine_mode(sentiment_state)
    day_data = config_data.get(weekday, {})
    print(f"☀️  Daytime mode: {mode}")

    week_pref = day_data.get("preference", "unknown")
    lookahead_minutes = settings.get("lookahead_minutes", 30)

    time_pref = get_current_trend_for_now(config_data, weekday, mode, now, lookahead_minutes)
    if not time_pref:
        fallback = get_current_trend_for_now(config_data, weekday, "default", now, lookahead_minutes)
        time_pref = fallback or "unknown"

    return {
        "weekday": weekday,
        "week_preference": week_pref,
        "time_preference": time_pref,
        "sentiment_mode": mode
    }

def analyze_datetime_preferences(current_time=None):
    """
    Palauttaa week_preference ja time_preference nykyhetken tai annetun ajan perusteella.
    
    :param current_time: datetime, oletuksena nykyhetki LOCAL_TIMEZONE:ssa
    :return: dict {
        "weekday": str,
        "week_preference": str,
        "time_preference": str,
        "sentiment_mode": str
    }
    """
    if current_time is None:
        current_time = datetime.now(LOCAL_TIMEZONE)

    weekday = current_time.strftime("%A")
    config_data, settings = load_config()
    sentiment_state = get_latest_sentiment_state()

    return get_preferences(config_data, weekday, current_time, sentiment_state, settings)

if __name__ == "__main__":
    try:
        # Kutsu funktio analyzoimaan aika-preferencet
        prefs = analyze_datetime_preferences()

        print(f"\n📅 Weekday: {prefs['weekday']}")
        print(f"📌 Week preference: {prefs['week_preference'].upper()}")
        print(f"🧠 Sentiment mode: {prefs['sentiment_mode'].upper()}")
        print(f"🕰️  Time-based preference: {prefs['time_preference'].upper()}")

    except Exception as e:
        print(f"❌ Error: {e}")
