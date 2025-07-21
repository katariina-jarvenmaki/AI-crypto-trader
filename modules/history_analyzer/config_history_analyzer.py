
CONFIG = {
    "history_log_path": "../AI-crypto-trader-logs/analysis-data/history_data_log.jsonl",
    "analysis_log_path": "../AI-crypto-trader-logs/analysis-data/history_analysis_log.jsonl",
    "sentiment_log_path": "../AI-crypto-trader-logs/analysis-data/history_sentiment_log.jsonl", 
    "symbol_log_path": "../AI-crypto-trader-logs/analysis-data/symbol_data_log.jsonl",
    "ohlcv_log_path": "../AI-crypto-trader-logs/fetched-data/ohlcv_fetch_log.jsonl",
    "price_log_path": "../AI-crypto-trader-logs/fetched-data/price_data_log.jsonl",
    "analysis_daily_logs_path": "../AI-crypto-trader-logs/analysis-data/daily/",
    "analysis_weekly_logs_path": "../AI-crypto-trader-logs/analysis-data/weekly/",
    "analysis_monthly_logs_path": "../AI-crypto-trader-logs/analysis-data/mothly/",
    "intervals_to_use": ["1h", "4h", "1d", "1w"],
    "min_prev_entry_age_minutes": 60, # prev-data aikaraja minuutteinan, minimi 60 min
    "ema_alpha": 0.2,
    "rsi_divergence_window": 2,
    "rsi_change_threshold": 1.0,
    "price_change_threshold": 1.0, # %
    "macd_diff_threshold": 0.4,
    "symbol_keys": ["potential_both_ways", "potential_to_long", "potential_to_short"],
}
