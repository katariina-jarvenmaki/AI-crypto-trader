
CONFIG = {
    "history_log_path": "modules/history_analyzer/history_data_log.jsonl",
    "symbol_log_path": "modules/symbol_data_fetcher/symbol_data_log.jsonl",
    "ohlcv_log_path": "integrations/multi_interval_ohlcv/ohlcv_fetch_log.jsonl",
    "price_log_path": "integrations/price_data_fetcher/price_data_log.jsonl",
    "daily_logs_path": "modules/history_analyzer/logs/",
    "intervals_to_use": ["1m", "1h", "4h", "1d", "1w"],
    "price_change_threshold": 2.0, # %
    "rsi_change_threshold": 2.0,
    "ema_alpha": 0.2,
    "macd_diff_threshold": 0.5,
    "rsi_divergence_window": 2,
    "symbol_keys": ["potential_both_ways", "potential_to_long", "potential_to_short"],
}
