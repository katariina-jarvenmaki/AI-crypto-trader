import json
from datetime import datetime, timedelta
from dateutil.parser import isoparse

from integrations.bybit_api_client import get_bybit_symbol_price, has_open_limit_order
from trade.execute_bybit_long import execute_bybit_long
from trade.execute_bybit_short import execute_bybit_short
from scripts.order_limiter import can_initiate, load_initiated_orders, normalize_symbol
from scripts.trade_order_logger import log_trade, log_skipped_order


def get_latest_log_entry_for_symbol(log_path: str, symbol: str) -> dict:
    with open(log_path, "r") as f:
        for line in reversed(f.readlines()):
            try:
                entry = json.loads(line)
                if entry.get("symbol") == symbol:
                    return entry
            except json.JSONDecodeError:
                continue
    return None

def get_latest_two_log_entries_for_symbol(log_path: str, symbol: str) -> list:
    entries = []
    with open(log_path, "r") as f:
        for line in reversed(f.readlines()):
            try:
                entry = json.loads(line)
                if entry.get("symbol") == symbol:
                    entries.append(entry)
                    if len(entries) == 2:
                        break
            except json.JSONDecodeError:
                continue
    return entries


def handle_unsupported_symbol(symbol, long_only, short_only, selected_symbols=None):
    print(f"⚠️  Symbol {symbol} is not in SUPPORTED_SYMBOLS. Handling accordingly.")
    selected_symbols = selected_symbols or [symbol]
    bybit_symbol = normalize_symbol(symbol)
    live_price = get_bybit_symbol_price(bybit_symbol)

    if not live_price:
        print(f"❌ Failed to get live price for {bybit_symbol}")
        return

    print(f"📈 Live price for {bybit_symbol}: {live_price:.4f} USDT")

    latest_entry = next(iter(get_latest_two_log_entries_for_symbol(
        "modules/history_analyzer/logs/history_analysis_log.jsonl", bybit_symbol)), None)

    if not latest_entry:
        print(f"❌ No history data for {bybit_symbol}, skipping trade.")
        return

    ohlcv_entry = get_latest_log_entry_for_symbol(
        "integrations/multi_interval_ohlcv/ohlcv_fetch_log.jsonl", bybit_symbol)
    price_entry = get_latest_log_entry_for_symbol(
        "integrations/price_data_fetcher/price_data_log.jsonl", bybit_symbol)
    sentiment_entry = get_latest_log_entry(
        "modules/history_analyzer/logs/history_sentiment_log.jsonl")
 
    price_data = price_entry.get("data_preview", {}) if price_entry else {}
    turnover = price_data.get("turnover")
    volume = price_data.get("volume")
    last_price = price_data.get("last_price")
    price_change_percent = price_data.get("price_change_percent")

    def log_and_skip(reason, direction, details):
        log_skipped_order(
            symbol=bybit_symbol,
            reason=reason,
            direction=direction,
            details=details,
            order_data={
                "price": live_price,
                "qty": None,
                "cost": None,
                "leverage": None,
                "ohlcv_data": ohlcv_entry,
                "price_data": price_entry,
                "history_analysis_data": latest_entry,
                "history_sentiment": sentiment_entry
            }
        )

    # --- Aikaehdot ---
    try:
        entry_time = isoparse(latest_entry.get("timestamp"))
        if datetime.now(entry_time.tzinfo) - entry_time > timedelta(hours=2):
            log_and_skip("Latest history entry is older than 2 hours.")
            print(f"⏳ Skipping {bybit_symbol}: latest history entry is older than 2 hours.")
            return
    except Exception as e:
        print(f"❌ Failed to parse timestamp for {bybit_symbol}: {e}")
        return

    if short_only:

        macd_trend = latest_entry.get("macd_trend")
        if macd_trend == "bullish":
            log_and_skip("MACD-trendi on bullish – shorttaus estetty", "short", {"macd_trend": macd_trend})
            print(f"⛔ Skipping SHORT: MACD-trendi on bullish.")
            return

        data_1h = ohlcv_entry.get("data_preview", {}).get("1h", {})
        data_15m = ohlcv_entry.get("data_preview", {}).get("15m", {})
        rsi_1h = data_1h.get("rsi")
        rsi_15m = data_15m.get("rsi")
        macd = data_1h.get("macd")
        macd_signal = data_1h.get("macd_signal")
        macd_diff = macd - macd_signal if macd is not None and macd_signal is not None else None

        allow_short = (
            (rsi_1h > 75 and macd_diff <= 0) or
            (rsi_1h > 75 and rsi_15m < 65)
        ) if rsi_1h and macd_diff is not None else False

        if not allow_short:
            log_and_skip("RSI/MACD suodatin: ei shorttia – trendi liian vahva", "short",
                         {"rsi_1h": rsi_1h, "rsi_15m": rsi_15m, "macd_diff": macd_diff})
            print("⛔ Skipping SHORT: RSI/MACD suodatin esti position avaamisen.")
            return

        bb_upper = data_1h.get("bb_upper")
        if bb_upper and last_price < bb_upper * 1.03:
            log_and_skip("BB-suodatin: hinta ei selvästi ylä-BB:n yläpuolella", "short",
                         {"last_price": last_price, "bb_upper_1h": bb_upper})
            print(f"⛔ Skipping SHORT: last_price ({last_price}) ei selvästi ylä-BB:n ({bb_upper}) yläpuolella.")
            return

        try:
            avg_price = turnover / volume if turnover and volume else None
            if avg_price and last_price < avg_price * 1.03 and price_change_percent > 35:
                log_and_skip("Price below avg_price after big move – possible premature short", "short",
                             {"avg_price": round(avg_price, 6), "last_price": last_price,
                              "price_change_percent": price_change_percent})
                print(f"📉 Skipping SHORT: last_price ({last_price}) < 95% of avg_price ({avg_price:.6f}) and price_change_percent {price_change_percent:.2f}%")
                return
        except Exception as e:
            print(f"⚠️ Failed turnover/volume filter for {bybit_symbol}: {e}")

        if not can_initiate(bybit_symbol, "short", load_initiated_orders(), selected_symbols):
            print(f"⛔ Skipping {bybit_symbol} short: too many initiations compared to others.")
            return

        if has_open_limit_order(bybit_symbol, "Sell"):
            print(f"⛔ Skipping {bybit_symbol} short: open limit order already exists.")
            return

        result = execute_bybit_short(symbol=bybit_symbol, risk_strength="strong")
        if result:
            log_trade(
                symbol=result["symbol"],
                platform="ByBit",
                direction="short",
                qty=result["qty"],
                price=result["price"],
                cost=result["cost"],
                leverage=result["leverage"],
                order_take_profit=result["tp_price"],
                order_stop_loss=result["sl_price"],
                ohlcv_data=ohlcv_entry,
                price_data=price_entry,
                history_analysis_data=latest_entry,
                history_sentiment=sentiment_entry
            )

    elif long_only:

        macd_trend = latest_entry.get("macd_trend")
        if macd_trend == "bearish":
            log_and_skip("MACD-trendi on bearish – longaus estetty", "long", {"macd_trend": macd_trend})
            print(f"⛔ Skipping LONG: MACD-trendi on bearish.")
            return

        data_1h = ohlcv_entry.get("data_preview", {}).get("1h", {})
        data_2h = ohlcv_entry.get("data_preview", {}).get("2h", {})
        rsi_2h = data_2h.get("rsi")

        if rsi_2h is not None and rsi_2h > 75:
            log_and_skip(f"RSI 2h liian korkea ({rsi_2h})", "long", {"rsi_2h": rsi_2h})
            print(f"📈 Skipping LONG: 2h RSI too high ({rsi_2h}).")
            return

        bb_lower = data_1h.get("bb_lower")
        if bb_lower and last_price > bb_lower * 1.02:
            log_and_skip("BB-suodatin: hinta ei selvästi ala-BB:n alapuolella", "long",
                        {"last_price": last_price, "bb_lower_1h": bb_lower})
            print(f"⛔ Skipping LONG: last_price ({last_price}) ei selvästi ala-BB:n ({bb_lower}) alapuolella.")
            return

        try:
            avg_price = turnover / volume if turnover and volume else None
            if avg_price and last_price > avg_price * 1.08 and price_change_percent > 40:
                log_and_skip("Price above avg_price after strong move – possible late long entry", "long",
                            {"avg_price": round(avg_price, 6), "last_price": last_price,
                            "price_change_percent": price_change_percent})
                print(f"📈 Skipping LONG: last_price ({last_price}) > 108% of avg_price ({avg_price:.6f}) and price_change_percent {price_change_percent:.2f}%")
                return
        except Exception as e:
            print(f"⚠️ Failed turnover/volume filter for {bybit_symbol}: {e}")

        if not can_initiate(bybit_symbol, "long", load_initiated_orders(), selected_symbols):
            print(f"⛔ Skipping {bybit_symbol} long: too many initiations compared to others.")
            return

        if has_open_limit_order(bybit_symbol, "Buy"):
            print(f"⛔ Skipping {bybit_symbol} long: open limit order already exists.")
            return

        # Median rsi check
        data_1m = ohlcv_entry.get("data_preview", {}).get("1m", {})
        data_5m = ohlcv_entry.get("data_preview", {}).get("5m", {})
        data_15m = ohlcv_entry.get("data_preview", {}).get("15m", {})

        rsi_1m = data_1m.get("rsi")
        rsi_5m = data_5m.get("rsi")
        rsi_15m = data_15m.get("rsi")

        short_rsi_values = [r for r in [rsi_1m, rsi_5m, rsi_15m] if r is not None]

        if macd_trend == "neutral":
            if short_rsi_values:
                rsi_median = sorted(short_rsi_values)[len(short_rsi_values)//2]

                if rsi_median > 85:
                    log_and_skip("RSI (1-15m) mediaani liian korkea – vältetään top long", "long",
                                {"rsi_1m": rsi_1m, "rsi_5m": rsi_5m, "rsi_15m": rsi_15m})
                    print(f"⛔ Skipping LONG: short-term RSI:t liian kuumat. (mediaani: {rsi_median:.2f})")
                    return

                if rsi_1m and rsi_5m and rsi_1m > 80 and rsi_5m > 80:
                    log_and_skip("RSI 1m ja 5m molemmat > 80 – mahdollinen spike", "long",
                                {"rsi_1m": rsi_1m, "rsi_5m": rsi_5m})
                    print(f"⛔ Skipping LONG: RSI 1m ({rsi_1m}) ja 5m ({rsi_5m}) molemmat > 80.")
                    return

        result = execute_bybit_long(symbol=bybit_symbol, risk_strength="strong")
        if result:
            price_entry = get_latest_log_entry_for_symbol(
                "integrations/price_data_fetcher/price_data_log.jsonl", bybit_symbol)
            log_trade(
                symbol=result["symbol"],
                platform="ByBit",
                direction="long",
                qty=result["qty"],
                price=result["price"],
                cost=result["cost"],
                leverage=result["leverage"],
                order_take_profit=result["tp_price"],
                order_stop_loss=result["sl_price"],
                ohlcv_data=ohlcv_entry,
                price_data=price_entry,
                history_analysis_data=latest_entry,
                history_sentiment= sentiment_entry
            )
    else:
        print(f"⚠️  Skipping: No direction specified.")

import json

def get_latest_log_entry(filepath):
    """Palauttaa tiedoston viimeisen JSONL-rivin dict-muodossa."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return None
            return json.loads(lines[-1])
    except Exception as e:
        print(f"Virhe logia luettaessa: {e}")
        return None
