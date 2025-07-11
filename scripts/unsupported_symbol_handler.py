from integrations.bybit_api_client import get_bybit_symbol_price, has_open_limit_order
from trade.execute_bybit_long_limit import execute_bybit_long_limit
from trade.execute_bybit_short_limit import execute_bybit_short_limit
from scripts.order_limiter import can_initiate, load_initiated_orders, normalize_symbol
from scripts.trade_order_logger import log_trade
import json

# Muokattavat hintavaihtelurajat prosentteina (esim. 0.04 = 4 %)
LONG_PRICE_OFFSET_PERCENT = -0.04
SHORT_PRICE_OFFSET_PERCENT = 0.04

def handle_unsupported_symbol(symbol, long_only, short_only, selected_symbols=None):

    print(f"⚠️  Symbol {symbol} is not in SUPPORTED_SYMBOLS. Handling accordingly.")

    if selected_symbols is None:
        selected_symbols = [symbol]  # fallback, tarvitaan order limiterille

    # Korvataan USDC → USDT jos tarpeen
    bybit_symbol = normalize_symbol(symbol)
    live_price = get_bybit_symbol_price(bybit_symbol)

    if not live_price:
        print(f"❌ Failed to get live price for {bybit_symbol}")
        return None

    print(f"📈 Live price for {bybit_symbol}: {live_price:.4f} USDT")

    # Lataa jo aloitetut tilaukset ja tarkista rajat
    initiated_counts = load_initiated_orders()

    if short_only is True:
        direction = "short"

        if not can_initiate(bybit_symbol, direction, initiated_counts, all_symbols=selected_symbols):
            print(f"⛔ Skipping {bybit_symbol} {direction}: too many initiations compared to others.")
            return

        if has_open_limit_order(bybit_symbol, "Sell"):
            print(f"⛔ Skipping {bybit_symbol} {direction}: open limit order already exists.")
            return

        target_price = live_price * (1 + SHORT_PRICE_OFFSET_PERCENT)
        print(f"📉 Short signal: Placing LIMIT SHORT @ {target_price:.4f}")

        bybit_result = execute_bybit_short_limit(symbol=bybit_symbol, risk_strength="strong")
        if bybit_result:

            # Hae viimeisimmät logitiedot
            bybit_symbol = symbol.replace("USDC", "USDT")
            ohlcv_entry = get_latest_log_entry_for_symbol("integrations/multi_interval_ohlcv/ohlcv_fetch_log.jsonl", bybit_symbol)
            price_entry = get_latest_log_entry_for_symbol("integrations/price_data_fetcher/price_data_log.jsonl", bybit_symbol)
            history_entry = get_latest_log_entry_for_symbol("modules/history_analyzer/history_data_log.jsonl", bybit_symbol)
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
                history_data=history_entry
            )

    elif long_only is True:
        direction = "long"

        if not can_initiate(bybit_symbol, direction, initiated_counts, all_symbols=selected_symbols):
            print(f"⛔ Skipping {bybit_symbol} {direction}: too many initiations compared to others.")
            return

        if has_open_limit_order(bybit_symbol, "Buy"):
            print(f"⛔ Skipping {bybit_symbol} {direction}: open limit order already exists.")
            return

        target_price = live_price * (1 + LONG_PRICE_OFFSET_PERCENT)
        print(f"📈 Long signal: Placing LIMIT LONG @ {target_price:.4f}")

        bybit_result = execute_bybit_long_limit(symbol=bybit_symbol, risk_strength="strong")
        if bybit_result:
            log_trade(
                symbol=bybit_result["symbol"],
                platform="ByBit",
                direction="long",
                qty=bybit_result["qty"],
                price=bybit_result["price"],
                cost=bybit_result["cost"],
                leverage=bybit_result["leverage"],
                order_take_profit=bybit_result["tp_price"],
                order_stop_loss=bybit_result["sl_price"]
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
    