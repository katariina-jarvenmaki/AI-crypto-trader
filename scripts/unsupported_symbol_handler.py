from integrations.bybit_api_client import get_bybit_symbol_price, has_open_limit_order
from trade.execute_bybit_long import execute_bybit_long
from trade.execute_bybit_short import execute_bybit_short
from scripts.order_limiter import can_initiate, load_initiated_orders, normalize_symbol
from scripts.trade_order_logger import log_trade
import json

from datetime import datetime, timedelta
from dateutil.parser import isoparse

def handle_unsupported_symbol(symbol, long_only, short_only, selected_symbols=None):

    print(f"⚠️  Symbol {symbol} is not in SUPPORTED_SYMBOLS. Handling accordingly.")

    if selected_symbols is None:
        selected_symbols = [symbol]

    bybit_symbol = normalize_symbol(symbol)
    live_price = get_bybit_symbol_price(bybit_symbol)

    if not live_price:
        print(f"❌ Failed to get live price for {bybit_symbol}")
        return None

    print(f"📈 Live price for {bybit_symbol}: {live_price:.4f} USDT")

    history_entries = get_latest_two_log_entries_for_symbol(
        "modules/history_analyzer/history_data_log.jsonl", bybit_symbol
    )

    if not history_entries:
        print(f"❌ No history data for {bybit_symbol}, skipping trade.")
        return None

    latest_entry = history_entries[0]
    previous_entry = history_entries[1] if len(history_entries) > 1 else {}

    # --- 🔎 Tarkista aikaehdot ---
    try:
        entry_time = isoparse(latest_entry.get("timestamp"))
        if datetime.now(entry_time.tzinfo) - entry_time > timedelta(hours=2):
            print(f"⏳ Skipping {bybit_symbol}: latest history entry is older than 2 hours.")
            return
    except Exception as e:
        print(f"❌ Failed to parse timestamp for {bybit_symbol}: {e}")
        return

    rsi_divergence = latest_entry.get("rsi_divergence")
    latest_flag = latest_entry.get("flag", "neutral")
    previous_flag = previous_entry.get("flag", "neutral")

    # ----- SHORT -----
    if short_only is True:

        # 🔴 Volume-tarkistus
        volume = latest_entry.get("volume")
        print(f"Volume: {volume}")
        if volume is not None and volume > 18000000:
            print(f"📉 Skipping SHORT: volume too high ({volume}).")
            return

        if not (
            rsi_divergence == "bearish-divergence" or 
            (latest_flag == "bear-flag" and previous_flag != "bear-flag")
        ):
            print(f"⛔ Skipping SHORT: conditions not met (rsi_divergence={rsi_divergence}, latest_flag={latest_flag}, previous_flag={previous_flag})")
            return

        direction = "short"

        initiated_counts = load_initiated_orders()
        if not can_initiate(bybit_symbol, direction, initiated_counts, all_symbols=selected_symbols):
            print(f"⛔ Skipping {bybit_symbol} {direction}: too many initiations compared to others.")
            return

        if has_open_limit_order(bybit_symbol, "Sell"):
            print(f"⛔ Skipping {bybit_symbol} {direction}: open limit order already exists.")
            return

        bybit_result = execute_bybit_short(symbol=bybit_symbol, risk_strength="strong")
        if bybit_result:
            ohlcv_entry = get_latest_log_entry_for_symbol("integrations/multi_interval_ohlcv/ohlcv_fetch_log.jsonl", bybit_symbol)
            price_entry = get_latest_log_entry_for_symbol("integrations/price_data_fetcher/price_data_log.jsonl", bybit_symbol)
            log_trade(
                symbol=bybit_result["symbol"],
                platform="ByBit",
                direction="short",
                qty=bybit_result["qty"],
                price=bybit_result["price"],
                cost=bybit_result["cost"],
                leverage=bybit_result["leverage"],
                order_take_profit=bybit_result["tp_price"],
                order_stop_loss=bybit_result["sl_price"],
                ohlcv_data=ohlcv_entry,
                price_data=price_entry,
                history_data=latest_entry
            )

    # ----- LONG -----
    elif long_only is True:

        # 🟠 RSI-tarkistus
        ohlcv_entry = get_latest_log_entry_for_symbol("integrations/multi_interval_ohlcv/ohlcv_fetch_log.jsonl", bybit_symbol)
        if ohlcv_entry:
            rsi_2h = ohlcv_entry.get("data_preview", {}).get("2h", {}).get("rsi")
            if rsi_2h is not None and rsi_2h > 70:
                print(f"📈 Skipping LONG: 2h RSI too high ({rsi_2h}).")
                return

        if not (
            rsi_divergence == "bullish-divergence" or 
            (latest_flag == "bull-flag" and previous_flag != "bull-flag")
        ):
            print(f"⛔ Skipping LONG: conditions not met (rsi_divergence={rsi_divergence}, latest_flag={latest_flag}, previous_flag={previous_flag})")
            return

        direction = "long"

        initiated_counts = load_initiated_orders()
        if not can_initiate(bybit_symbol, direction, initiated_counts, all_symbols=selected_symbols):
            print(f"⛔ Skipping {bybit_symbol} {direction}: too many initiations compared to others.")
            return

        if has_open_limit_order(bybit_symbol, "Buy"):
            print(f"⛔ Skipping {bybit_symbol} {direction}: open limit order already exists.")
            return

        bybit_result = execute_bybit_long(symbol=bybit_symbol, risk_strength="strong")
        if bybit_result:
            price_entry = get_latest_log_entry_for_symbol("integrations/price_data_fetcher/price_data_log.jsonl", bybit_symbol)
            log_trade(
                symbol=bybit_result["symbol"],
                platform="ByBit",
                direction="long",
                qty=bybit_result["qty"],
                price=bybit_result["price"],
                cost=bybit_result["cost"],
                leverage=bybit_result["leverage"],
                order_take_profit=bybit_result["tp_price"],
                order_stop_loss=bybit_result["sl_price"],
                ohlcv_data=ohlcv_entry,
                price_data=price_entry,
                history_data=latest_entry
            )

    else:
        print(f"⚠️  Skipping: No direction specified.")
        return None

def get_latest_log_entry_for_symbol(log_path: str, symbol: str) -> dict:
    latest_entry = None
    with open(log_path, "r") as f:
        for line in reversed(f.readlines()):
            try:
                entry = json.loads(line)
                if entry.get("symbol") == symbol:
                    latest_entry = entry
                    break
            except json.JSONDecodeError:
                continue
    return latest_entry
    
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