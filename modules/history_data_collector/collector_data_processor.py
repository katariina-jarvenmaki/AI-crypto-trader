# modules/history_data_collector/collector_data_processor.py
# version 2.0, aug 2025

from utils.get_timestamp import get_timestamp

def collector_data_processor(symbol, ohlcv_entry, price_entry, log_path):

    timestamp = get_timestamp()

    # Get the price data
    price_data = price_entry or ohlcv_entry.get("data_preview", {}).get("price_data", {})
    price = price_data.get("last_price")
    change_24h = price_data.get("price_change_percent")
    high_price = price_data.get("high_price")
    low_price = price_data.get("low_price")
    volume = price_data.get("volume")
    turnover = price_data.get("turnover")

    print(f"symbol: {symbol}")
    print(f"timestamp: {timestamp}")
    print(f"== Price data ==")
    print(f"price: {price}")
    print(f"change_24h: {change_24h}")
    print(f"high_price: {high_price}")
    print(f"low_price: {low_price}")
    print(f"volume: {volume}")
    print(f"turnover: {turnover}")
    print(f"== Raw ==")
    print(f"ohlcv_entry: {ohlcv_entry}")
    print(f"price_entry: {price_entry}")
    print(f"log_path: {log_path}")
    print(f"price_data: {price_data}")

    # Kerätään indikaattoridatat kaikille intervalleille
    # rsi = {i: ohlcv_entry["data_preview"].get(i, {}).get("rsi") for i in CONFIG["intervals_to_use"]}
    # ema = {i: ohlcv_entry["data_preview"].get(i, {}).get("ema") for i in CONFIG["intervals_to_use"]}
    # macd = {i: ohlcv_entry["data_preview"].get(i, {}).get("macd") for i in CONFIG["intervals_to_use"]}
    # macd_signal = {i: ohlcv_entry["data_preview"].get(i, {}).get("macd_signal") for i in CONFIG["intervals_to_use"]}
    # bb_upper = {i: ohlcv_entry["data_preview"].get(i, {}).get("bb_upper") for i in CONFIG["intervals_to_use"]}
    # bb_lower = {i: ohlcv_entry["data_preview"].get(i, {}).get("bb_lower") for i in CONFIG["intervals_to_use"]}

    # Keskiarvofunktio (jättää pois None-arvot)
    # def avg(values):
    #     vals = [v for v in values if v is not None]
    #     return sum(vals) / len(vals) if vals else None

    # Lasketaan kaikki keskiarvot
    # avg_rsi_all = avg(rsi.values())
    # avg_rsi_1h_4h = avg([rsi.get("1h"), rsi.get("4h")])
    # avg_rsi_1d_1w = avg([rsi.get("1d"), rsi.get("1w")])

    # avg_macd_all = avg(macd.values())
    # avg_macd_1h_4h = avg([macd.get("1h"), macd.get("4h")])
    # avg_macd_1d_1w = avg([macd.get("1d"), macd.get("1w")])

    # avg_macd_signal_all = avg(macd_signal.values())
    # avg_macd_signal_1h_4h = avg([macd_signal.get("1h"), macd_signal.get("4h")])
    # avg_macd_signal_1d_1w = avg([macd_signal.get("1d"), macd_signal.get("1w")])

    # EMA-arvot keskiarvoina
    # ema_rsi = avg_rsi_all  # oletuksena sama kuin avg_rsi_all, muuta jos laskenta erilainen
    # ema_macd = avg_macd_all
    # ema_macd_signal = avg_macd_signal_all

    # MACD diff
    # macd_diff = (avg_macd_all - avg_macd_signal_all) if avg_macd_all is not None and avg_macd_signal_all is not None else None

    # Lopullinen dict vanhan formaatin mukaisesti
    # parsed = {
    #     "timestamp": timestamp,
    #     "symbol": symbol,
    #     "price": price_data.get("last_price"),
    #     "high_price": price_data.get("high_price"),
    #     "low_price": price_data.get("low_price"),
    #     "volume": price_data.get("volume"),
    #     "turnover": price_data.get("turnover"),
    #     "change_24h": price_data.get("price_change_percent"),
    #     "rsi": rsi,
    #     "ema": ema,
    #     "macd": macd,
    #     "macd_signal": macd_signal,
    #     "bb_upper": bb_upper,
    #     "bb_lower": bb_lower,
    #     "avg_rsi_all": avg_rsi_all,
    #     "avg_rsi_1h_4h": avg_rsi_1h_4h,
    #     "avg_rsi_1d_1w": avg_rsi_1d_1w,
    #     "avg_macd_all": avg_macd_all,
    #     "avg_macd_1h_4h": avg_macd_1h_4h,
    #     "avg_macd_1d_1w": avg_macd_1d_1w,
    #     "avg_macd_signal_all": avg_macd_signal_all,
    #     "avg_macd_signal_1h_4h": avg_macd_signal_1h_4h,
    #     "avg_macd_signal_1d_1w": avg_macd_signal_1d_1w,
    #     "ema_rsi": ema_rsi,
    #     "ema_macd": ema_macd,
    #     "ema_macd_signal": ema_macd_signal,
    #     "macd_diff": macd_diff,
    # }

    # print(f"Parsed: {parsed}")
    # return parsed