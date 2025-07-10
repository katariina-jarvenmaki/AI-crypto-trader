# integrations/price_data_fetcher/config_price_data_fetcher.py

CONFIG = {
    "symbol_log_path": "modules/symbol_data_fetcher/symbol_data_log.jsonl",
    "symbol_keys": ["potential_both_ways", "potential_to_long", "potential_to_short"],
    "exchange_priority": ["okx", "kucoin", "binance", "bybit"],
    "price_data_log_path": "integrations/price_data_fetcher/price_data_log.jsonl",
    "max_log_lines": 10000,
}
