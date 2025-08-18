# modules/history_data_collector/collector_data_processor.py
# version 2.0, aug 2025

from utils.get_timestamp import get_timestamp

def collector_data_processor(symbol, history_config, ohlcv_entry, price_entry):

    timestamp = get_timestamp()

    # Get the price data
    price_data = price_entry or ohlcv_entry.get("data_preview", {}).get("price_data", {})
    price = price_data.get("last_price")
    change_24h = price_data.get("price_change_percent")
    high_price = price_data.get("high_price")
    low_price = price_data.get("low_price")
    volume = price_data.get("volume")
    turnover = price_data.get("turnover")

    # Get the ohlcv data
    intervals = ohlcv_entry.get("intervals")
    interval_data = ohlcv_entry.get("data_preview", {})

    # Get indicator data based on history_config intervals
    rsi_data = {
        interval: interval_data.get(interval, {}).get("rsi")
        for interval in history_config.get("history_data_collector", {}).get("intervals_to_use", [])
    }
    ema_data = {
        interval: interval_data.get(interval, {}).get("ema")
        for interval in history_config.get("history_data_collector", {}).get("intervals_to_use", [])
    }
    macd_data = {
        interval: interval_data.get(interval, {}).get("macd")
        for interval in history_config.get("history_data_collector", {}).get("intervals_to_use", [])
    }
    macd_signal_data = {
        interval: interval_data.get(interval, {}).get("macd_signal")
        for interval in history_config.get("history_data_collector", {}).get("intervals_to_use", [])
    }
    bb_upper = {
        interval: interval_data.get(interval, {}).get("bb_upper")
        for interval in history_config.get("history_data_collector", {}).get("intervals_to_use", [])
    }
    bb_lower = {
        interval: interval_data.get(interval, {}).get("bb_lower")
        for interval in history_config.get("history_data_collector", {}).get("intervals_to_use", [])
    }

    # Return all collected data as dict
    return {
        "timestamp": timestamp,
        "symbol": symbol,
        "rsi": rsi_data,
        "ema": ema_data,
        "macd": macd_data,
        "macd_signal": macd_signal_data,
        "bb_upper": bb_upper,
        "bb_lower": bb_lower,
        "fetched": {
            "price": price,
            "change_24h": change_24h,
            "high_price": high_price,
            "low_price": low_price,
            "volume": volume,
            "turnover": turnover,
            "intervals": intervals,
            "interval_data": interval_data
        }
    }

