# integrations/multi_interval_ohlcv/multi_ohlcv_handler.py

import logging
from configs.config import MULTI_INTERVAL_EXCHANGE_PRIORITY, DEFAULT_OHLCV_LIMIT, DEFAULT_INTERVALS
from integrations.multi_interval_ohlcv.fetch_ohlcv_okx_for_intervals import fetch_ohlcv_okx
from integrations.multi_interval_ohlcv.fetch_ohlcv_kucoin_for_intervals import fetch_ohlcv_kucoin
from integrations.multi_interval_ohlcv.fetch_ohlcv_bybit_for_intervals import fetch_ohlcv_bybit
from integrations.multi_interval_ohlcv.fetch_ohlcv_binance_for_intervals import fetch_ohlcv_binance

FETCH_FUNCTIONS = {
    'okx': fetch_ohlcv_okx,
    'kucoin': fetch_ohlcv_kucoin,
    'binance': fetch_ohlcv_binance,
    'bybit': fetch_ohlcv_bybit
}

def fetch_ohlcv_fallback(symbol, intervals=None, limit=None, start_time=None, end_time=None):
    intervals = intervals or DEFAULT_INTERVALS
    limit = limit or DEFAULT_OHLCV_LIMIT
    errors = {}

    for exchange in MULTI_INTERVAL_EXCHANGE_PRIORITY:
        fetch_fn = FETCH_FUNCTIONS.get(exchange)
        if not fetch_fn:
            logging.warning(f"[{exchange}] Ei määritetty fetch-funktiota.")
            continue

        try:
            logging.info(f"🔍 Yritetään hakea OHLCV-tietoja {symbol} ({intervals}) alustalta {exchange}")
            # Pass optional times to fetch functions
            data_by_interval, source_exchange = fetch_fn(
                symbol, intervals, limit=limit,
                start_time=start_time, end_time=end_time
            )

            if any(not df.empty for df in data_by_interval.values()):
                logging.info(f"✅ Haku onnistui: {symbol} ({source_exchange})")
                return data_by_interval, source_exchange
            else:
                errors[exchange] = "Tyhjät DataFramet"

        except Exception as e:
            errors[exchange] = str(e)
            logging.warning(f"⚠️ Virhe haettaessa {symbol} ({exchange}): {e}")

    logging.error(f"❌ OHLCV-tietojen haku epäonnistui kaikilta alustoilta. Virheet: {errors}")
    print(f"\033[93m⚠️ This coin pair can't be found from any supported exchange: {symbol}\033[0m")
    return None, None
