# modules/history_data_collector/collector_data_processor.py
# version 2.0, aug 2025

def collector_data_processor(symbol, ohlcv_entry, price_entry):

    # Lisätään price_entry:n hinnat ohlcv_entry:n sisään samaan tapaan kuin data_collector tekee
    ohlcv_entry = dict(ohlcv_entry)  # varmuuden vuoksi kopio
    ohlcv_entry["data_preview"] = dict(ohlcv_entry.get("data_preview", {}))
    ohlcv_entry["data_preview"]["price_data"] = {
        "last_price": price_entry.get("last_price"),
        "price_change_percent": price_entry.get("price_change_percent"),
        "high_price": price_entry.get("high_price"),
        "low_price": price_entry.get("low_price"),
        "volume": price_entry.get("volume"),
        "turnover": price_entry.get("turnover"),
    }

    # Haetaan hintatiedot
    price_data = ohlcv_entry["data_preview"]["price_data"]
    parsed = {
        "symbol": symbol,
        "timestamp": ohlcv_entry.get("timestamp"),
        "price": price_data.get("last_price"),
        "change_24h": price_data.get("price_change_percent"),
        "high_price": price_data.get("high_price"),
        "low_price": price_data.get("low_price"),
        "volume": price_data.get("volume"),
        "turnover": price_data.get("turnover"),
        # Haetaan indikaattorit määriteltyjen intervallien mukaan
        "rsi": {i: ohlcv_entry["data_preview"].get(i, {}).get("rsi") for i in CONFIG["intervals_to_use"]},
        "ema": {i: ohlcv_entry["data_preview"].get(i, {}).get("ema") for i in CONFIG["intervals_to_use"]},
        "macd": {i: ohlcv_entry["data_preview"].get(i, {}).get("macd") for i in CONFIG["intervals_to_use"]},
        "macd_signal": {i: ohlcv_entry["data_preview"].get(i, {}).get("macd_signal") for i in CONFIG["intervals_to_use"]},
        "bb_upper": {i: ohlcv_entry["data_preview"].get(i, {}).get("bb_upper") for i in CONFIG["intervals_to_use"]},
        "bb_lower": {i: ohlcv_entry["data_preview"].get(i, {}).get("bb_lower") for i in CONFIG["intervals_to_use"]},
    }

    print(f"Parsed: {parsed}")