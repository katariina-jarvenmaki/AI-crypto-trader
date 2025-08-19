# modules/history_analyzer/analysis_engine.py
# version 2.0, aug 2025

from typing import List, Dict
from utils.get_timestamp import get_timestamp

def analyze_log_data(symbol, latest, previous):

    print(f"\n🔍 Analyzing symbol: {symbol}")
    print(f"⏱ Time: {latest['timestamp']}  vs.  {previous['timestamp']}")
    timestamp = get_timestamp()
    fetched = latest["fetched"]

    def calc_change_and_percent(current, prev):
        current = float(current)
        prev = float(prev)
        try:
            delta = current - prev
            percent = (delta / prev) * 100 if prev != 0 else None
            return delta, percent
        except TypeError:
            print(f"⚠️ Cannot calculate change: current={current} ({type(current)}), prev={prev} ({type(prev)})")
            return None, None

    # Price Data
    # price = fetched["price"]
    # prev_price = previous["price"]
    # price_change, price_change_percent = calc_change_and_percent(price, prev_price)
    
    # RSI Data
    # avg_rsi = sum(latest["rsi"].values()) / len(latest["rsi"])
    # prev_rsi = previous.get("avg_rsi")
    # rsi_change, rsi_change_percent = calc_change_and_percent(avg_rsi, prev_rsi)

    # EMA Data
    # avg_ema = sum(latest["ema"].values()) / len(latest["ema"])
    # prev_avg_ema = previous.get("avg_ema")
    # ema_change, ema_change_percent = calc_change_and_percent(avg_ema, prev_avg_ema)

    # MACD Data
    # avg_macd = sum(latest["macd"].values()) / len(latest["macd"])
    # prev_macd = previous.get("avg_macd")
    # macd_change, macd_change_percent = calc_change_and_percent(macd, prev_macd)


    # print(f"macd: {macd}")
    # print(f"prev_macd: {prev_macd}")
    # print(f"macd_delta: {macd_delta}")
    # print(f"macd_percent: {macd_percent}")

    # Get Latest values
    # print(f"\n=== Latest ===")
    # print(f'timestamp: {latest["timestamp"]}')
    # print(f'symbol: {latest["symbol"]}')
    # print(f'rsi: {latest["rsi"]}')
    # print(f'ema: {latest["ema"]}')
    # print(f'macd: {latest["macd"]}')
    # print(f'macd_signal: {latest["macd_signal"]}')
    # print(f'bb_upper: {latest["bb_upper"]}')
    # print(f'bb_lower: {latest["bb_lower"]}')
    # print(f'price: {price}')
    # print(f'change_24h: {fetched["change_24h"]}')
    # print(f'high_price: {fetched["high_price"]}')
    # print(f'low_price: {fetched["low_price"]}')
    # print(f'volume: {fetched["volume"]}')
    # print(f'turnover: {fetched["turnover"]}')
    # print(f'intervals: {fetched["intervals"]}')
    # print(f'interval_data: {fetched["interval_data"]}')

    # Get Previous values
    # print(f"\n=== Previous ===")
    # print(f'timestamp: {previous["timestamp"]}')
    # print(f'symbol: {previous["symbol"]}')
    # print(f'price: {prev_price}')
    # print(f'price_change: {previous["price_change"]}')
    # print(f'price_change_percent: {previous["price_change_percent"]}')
    # print(f'avg_rsi_all: {previous["avg_rsi_all"]}')
    # print(f'rsi_change: {previous["rsi_change"]}')
    # print(f'rsi_change_percent: {previous["rsi_change_percent"]}')
    # print(f'rsi_delta: {previous["rsi_delta"]}')
    # print(f'ema_rsi: {previous["ema_rsi"]}')
    # print(f'ema_rsi_delta: {previous["ema_rsi_delta"]}')
    # print(f'ema_rsi_change_percent: {previous["ema_rsi_change_percent"]}')
    # print(f'macd: {previous["macd"]}')
    # print(f'macd_diff_change: {previous["macd_diff_change"]}')
    # print(f'macd_diff_change_percent: {previous["macd_diff_change_percent"]}')
    # print(f'macd_trend: {previous["macd_trend"]}')
    # print(f'bollinger_status: {previous["bollinger_status"]}')
    # print(f'ema_trend: {previous["ema_trend"]}')
    # print(f'signal_strength: {previous["signal_strength"]}')
    # print(f'flag: {previous["flag"]}')
    # print(f'turnover_status: {previous["turnover_status"]}')
    # print(f'rsi_divergence: {previous["rsi_divergence"]}')

    # Return values
    # print(f"\n=== Return ===")
    # print(f'timestamp: {timestamp}')
    # print(f'symbol: {symbol}')
    # print(f'price: {price}')
    # print(f'price_change: {price_change}')
    # print(f'price_change_percent: {price_change_percent}')
    # print(f'avg_rsi: {avg_rsi}')
    # print(f'rsi_change: {rsi_change}')
    # print(f'rsi_change_percent: {rsi_change_percent}')
    # print(f'rsi_delta: {rsi_delta}')
    # print(f'avg_ema: {avg_ema}')
    # print(f'ema_change: {ema_change}')
    # print(f'ema_change_percent: {ema_change_percent}')
    # print(f'avg_macd: {avg_macd}')
    # print(f'macd_change: {macd_change}')
    # print(f'macd_change_percent: {macd_change_percent}')
    # print(f'macd_trend: {macd_trend}')
    # print(f'bollinger_status: {bollinger_status}')
    # print(f'ema_trend: {ema_trend}')
    # print(f'signal_strength: {signal_strength}')
    # print(f'flag: {flag}')
    # print(f'turnover_status: {turnover_status}')
    # print(f'rsi_divergence: {rsi_divergence}')


    # print(f"⏱ Aika: {latest['timestamp']}  vs.  {previous['timestamp']}")

    # Helper
    # def calc_change_and_percent(current, prev):
    #     if current is None or prev is None:
    #         return None, None
    #     delta = current - prev
    #     percent = (delta / prev) * 100 if prev != 0 else None
    #     return delta, percent

    # --- Base info ---
    # price = latest["fetched"]["price"]
    # prev_price = previous["price"]

    # avg_rsi = sum(latest["rsi"].values()) / latest["rsi"]["1d"]
    # prev_avg_rsi = previous.get("avg_rsi_all")


    # print(f"latest: {latest}")
    # print(f"previous: {previous}")
    # print(f"{latest.get('rsi')}")
    # print(f"{sum(latest['rsi'].values())}")

    # print(f"{latest['rsi']['1d']}")
    # print(f"{avg_rsi}")
    # print(f"{prev_avg_rsi}")

    # print(f"previous: {previous}")
    # print(f"price: {price}")
    # print(f"prev_price: {prev_price}")


def analyze_latest_only(symbol, latest: dict) -> dict:
    """
    Analysoi symbolin tiedot vain viimeisimmän entryn perusteella (ilman previous-dataa).
    Palauttaa saman rakenteen kuin analyze_log_data, mutta vertailukentät = None.
    """
    print(f"\n🔍 Analysoidaan symbolia (vain latest): {symbol}")

    price = float(latest["fetched"]["price"])
    avg_rsi = sum(v for v in latest["rsi"].values() if v is not None) / max(
        1, len([v for v in latest["rsi"].values() if v is not None])
    )
    avg_ema = sum(v for v in latest["ema"].values() if v is not None) / max(
        1, len([v for v in latest["ema"].values() if v is not None])
    )

    macd_pairs = [
        (latest["macd"].get(k), latest["macd_signal"].get(k))
        for k in latest["macd"]
    ]
    macd_diffs = [
        macd - signal for macd, signal in macd_pairs if macd is not None and signal is not None
    ]
    avg_macd = sum(macd_diffs) / len(macd_diffs) if macd_diffs else None

    bollinger_status = analyze_bollinger(price, latest["bb_upper"]["1d"], latest["bb_lower"]["1d"])
    ema_trend = detect_ema_trend(price, latest["ema"]["1d"])
    macd_trend = detect_macd_trend(avg_macd)

    return {
        "symbol": symbol,
        "timestamp": latest["timestamp"],

        # Price
        "price": price,
        "price_change": None,
        "price_change_percent": None,

        # RSI
        "avg_rsi": avg_rsi,
        "rsi_change": None,
        "rsi_change_percent": None,

        # EMA
        "avg_ema": avg_ema,
        "ema_change": None,
        "ema_change_percent": None,

        # MACD
        "avg_macd": avg_macd,
        "macd_change": None,
        "macd_change_percent": None,

        # Trends and statuses
        "macd_trend": macd_trend,
        "bollinger_status": bollinger_status,
        "ema_trend": ema_trend,
        "signal_strength": None,
        "flag": None,

        # Analyses
        "turnover_status": None,
        "rsi_divergence": None,
    }

def analyze_bollinger(price, bb_upper, bb_lower):
    if price is None or bb_upper is None or bb_lower is None:
        return "unknown"
    if price >= bb_upper:
        return "overbought"
    elif price <= bb_lower:
        return "oversold"
    return "neutral"

def detect_ema_trend(price, ema_1d):
    if price is None or ema_1d is None:
        return "unknown"
    if price > ema_1d * 1.01:
        return "strong_above"
    elif price < ema_1d * 0.99:
        return "strong_below"
    return "near_ema"

def detect_turnover_anomaly(turnover, volume, price):
    if turnover is None or volume is None or price is None:
        return "invalid"
    if volume == 0:
        return "invalid"
    avg_price = turnover / volume
    deviation = abs(avg_price - price) / price
    return "mismatch" if deviation > 0.02 else "normal"

def detect_flag(prev_rsi, curr_rsi):
    if prev_rsi is None:
        return "neutral"
    if curr_rsi > prev_rsi + 5:
        return "bullish"
    elif curr_rsi < prev_rsi - 5:
        return "bearish"
    return "neutral"

def estimate_signal_strength(flag, macd_trend, bollinger_status, ema_trend):
    if flag == "bullish" and macd_trend == "bullish" and bollinger_status == "oversold" and ema_trend == "strong_above":
        return "very_strong_bullish"
    if flag == "bearish" and macd_trend == "bearish" and bollinger_status == "overbought" and ema_trend == "strong_below":
        return "very_strong_bearish"
    if flag != "neutral":
        return "watch_for_reversal"
    return "neutral"

def detect_macd_trend(macd_diff, threshold=0.01):
    if macd_diff is None or abs(macd_diff) < threshold:
        return "neutral"
    return "bullish" if macd_diff > 0 else "bearish"

def detect_rsi_divergence(history: List[Dict], current_avg: float) -> str:
    if len(history) < CONFIG["rsi_divergence_window"]:
        return "none"

    prev = history[-1]
    prev2 = history[-2]

    if prev["avg_rsi"] is None or prev2["avg_rsi"] is None or current_avg is None:
        return "none"

    if prev["avg_rsi"] > prev2["avg_rsi"] and current_avg < prev["avg_rsi"]:
        return "bearish-divergence"
    elif prev["avg_rsi"] < prev2["avg_rsi"] and current_avg > prev["avg_rsi"]:
        return "bullish-divergence"

    return "none"

def analysis_engine(symbol: str, history_config: Dict, collection_entry: Dict, analysis_entry: Dict):

    print("Analysis engine starting...")

    timestamp = get_timestamp()
    latest = collection_entry
    previous = analysis_entry if analysis_entry else None

    if previous:
        return analyze_log_data(symbol, latest, previous)
    else:
        return analyze_latest_only(symbol, latest)
