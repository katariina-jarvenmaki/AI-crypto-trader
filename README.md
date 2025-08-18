# AI-crypto-trader
Just a multiplatform AI crypto trader

## Install and Usage

**1. Install libraries**

```bash
pip3 install python-binance pandas pandas_ta ta scipy pybit numpy==1.26.4 matplotlib requests python-dateutil jsonschema pytest
```

**2. Make a credentials.py to configs-folder**

Contents:
```bash
# configs/credentials.py

# BINANCE API
BINANCE_API_KEY = 'your_api_key'
BINANCE_API_SECRET = 'your_secret_key'

# BYBIT - must to update
BYBIT_API_KEY = "your_real_api_key"
BYBIT_API_SECRET = "your_real_api_secret"

# BTCC API
BTCC_API_KEY = "your_api_key"
BTCC_SECRET_KEY = "your_secret_key"
BTCC_USERNAME = "your_email"
BTCC_PASSWORD = "your_password"
BTCC_COMPANYID = "1"
```
Input your own data...

**3. Setup the crons**

**Check and update crons**
```bash
crontab -e
```

**Add these lines to the cron (keep them separate)**
```bash
TZ=Europe/Helsinki

0 1,5,9,13,17,21 * * * cd /opt/kjc/int/AI-crypto-trader && flock -n /tmp/potential_trades_checker.lock -c "/usr/bin/python3 -m modules.symbol_data_fetcher.tasks.potential_trades_checker >> ../AI-crypto-trader-logs/cron/temporary_log_potential_trades_checker_cron.log 2>&1" || echo "$(date) potential_trades_checker skipped (already running)" >> ../AI-crypto-trader-logs/cron/temporary_log_potential_trades_checker_cron.log

*/1 * * * * cd /opt/kjc/int/AI-crypto-trader && flock -n /tmp/fetch_symbols_data.lock -c "/usr/bin/python3 -m modules.symbol_data_fetcher.tasks.fetch_symbols_data >> ../AI-crypto-trader-logs/cron/fetch_symbols_data.log 2>&1" || echo "$(date) fetch_symbols_data skipped (already running)" >> ../AI-crypto-trader-logs/cron/fetch_symbols_data.log

*/1 * * * * cd /opt/kjc/int/AI-crypto-trader && flock -n /tmp/price_data_fetcher.lock -c "/usr/bin/python3 -m integrations.price_data_fetcher.price_data_fetcher >> ../AI-crypto-trader-logs/cron/price_data_fetcher.log 2>&1" || echo \"$(date) price_data_fetcher skipped (already running)\" >> ../AI-crypto-trader-logs/cron/price_data_fetcher.log

*/1 * * * * cd /opt/kjc/int/AI-crypto-trader && flock -n /tmp/history_data_collector.lock -c "/usr/bin/python3 -m modules.history_data_collector.history_data_collector >> ../AI-crypto-trader-logs/cron/history_data_collector.log 2>&1" || echo "$(date) history_data_collector skipped (already running)" >> ../AI-crypto-trader-logs/cron/history_data_collector.log
```

**Check cron log**
```bash
tail -n 100 /opt/kjc/int/AI-crypto-trader-logs/cron/cron.log
```

**4. Run the datacollectors and analyzers or wait crons to run them**

To run Symbol data fetchers manually:
```bash
# 1. Run only potential_trades_checker
python3 -m modules.symbol_data_fetcher.symbol_data_fetcher potential_trades_checker

# 2. Run only fetch_symbols_data
python3 -m modules.symbol_data_fetcher.symbol_data_fetcher fetch_symbols_data

# 3. Run both in the correct order (first potential_trades_checker, then fetch_symbols_data)
python3 -m modules.symbol_data_fetcher.symbol_data_fetcher
```

To run price data fetchers and history analyzer manually:
```bash
cd /opt/kjc/int/AI-crypto-traderr
/usr/bin/python3 -m integrations.price_data_fetcher.price_data_fetcher
/usr/bin/python3 -m modules.history_data_collector.history_data_collector
/usr/bin/python3 -m modules.history_analyzer.history_analyzer
/usr/bin/python3 -m modules.master_balance_logger.master_balance_logger
```

**5. Start trading**

```bash
python3 main.py binance
```

**Usage guide**

Run the app on default platform (Binance) with default coinpair (BTCUSDC) and automatic market state detection
```bash
python3 main.py
```

Run the app on specified platform with automatic coinpair selection and automatic market state detection
```bash
python3 main.py binance
```

Force the buy / sell -signal to start buying / selling right away (it does it only for first coinpair "BTCUSDT" and only on first round):
```bash
python3 main.py buy
python3 main.py sell
```

Mode restrictions:
```bash
python3 main.py binance long-only
python3 main.py binance short-only
python3 main.py binance no-trade
python3 main.py binance no-stoploss
python3 main.py binance long-only no-stoploss
python3 main.py binance short-only no-stoploss
python3 main.py binance no-trade no-stoploss
```

To run Symbol data fetchers manually:
```bash
# 1. Run only potential_trades_checker
python3 -m modules.symbol_data_fetcher.symbol_data_fetcher potential_trades_checker

# 2. Run only fetch_symbols_data
python3 -m modules.symbol_data_fetcher.symbol_data_fetcher fetch_symbols_data

# 3. Run both in the correct order (first potential_trades_checker, then fetch_symbols_data)
python3 -m modules.symbol_data_fetcher.symbol_data_fetcher
```

To run Price Data Fetcher manually (supposted to be ran through cron_tasks_processor.py):
```bash
/usr/bin/python3 -m integrations.price_data_fetcher.price_data_fetcher
```

To run History analyzer manually  (supposted to be ran through cron_tasks_processor.py):
```bash
/usr/bin/python3 -m modules.history_data_collector.history_data_collector
/usr/bin/python3 -m modules.history_analyzer.history_analyzer
```

To run Master Balance logger manually (supposted to be ran through cron_tasks_processor.py):
```bash
/usr/bin/python3 -m modules.master_balance_logger.master_balance_logger
```

To run dublicate history log entry remover:
```bash
/usr/bin/python3 -m modules.history_analyzer.remove_duplicates_from_jsonl
```

**6. Testing**

Test Load and Validate manually:
```bash
/usr/bin/python3 -m modules.load_and_validate.load_and_validate
```

Test Path Selector manually:
```bash
/usr/bin/python3 -m modules.pathbuilder.path_selector
```

Test Get Filenames manually:
```bash
/usr/bin/python3 -m modules.pathbuilder.get_filenames
```

Test File Checker manually:
```bash
/usr/bin/python3 -m modules.save_and_validate.file_checker config.json
```

Test Pathbuilder manually:
```bash
/usr/bin/python3 -m modules.pathbuilder.pathbuilder
```

Test Get Timestamp manually:
```bash
/usr/bin/python3 -m utils.get_timestamp
```

Test Multi Ohlcv Handler manually:
```bash
/usr/bin/python3 -m integrations.multi_interval_ohlcv.multi_ohlcv_handler
```

Test Save and Validate manually:
```bash
/usr/bin/python3 -m modules.save_and_validate.save_and_validate
```

Test Load Latest Entry manually:
```bash
/usr/bin/python3 -m utils.load_latest_entry
```

Test Load Latest Entries per Symbol manually:
```bash
/usr/bin/python3 -m utils.load_latest_entries_per_symbol
```

Test Get Symbols to Use manually:
```bash
/usr/bin/python3 -m utils.get_symbols_to_use
```

Test Price Data Fetcher manually:
```bash
/usr/bin/python3 -m integrations.price_data_fetcher.price_data_fetcher
```

Test History Data Collector manually:
```bash
/usr/bin/python3 -m modules.history_data_collector.history_data_collector
```

Test Load Configs and Logs manually:
```bash
/usr/bin/python3 -m utils.load_configs_and_logs
```

Test Symbol Data Fetchers manually:
```bash
python3 -m modules.symbol_data_fetcher.tasks.potential_trades_checker
python3 -m modules.symbol_data_fetcher.tasks.fetch_symbols_data
python3 -m modules.symbol_data_fetcher.symbol_data_fetcher
```

Test Cron Tasks Prosessor manually:
```bash
/usr/bin/python3 -m core.cron_tasks_processor
```

Test Binance-integration status
```bash
python3 integrations/binance_api_client.py
```

Test BTCC-integration status
```bash
python3 integrations/btcc_api_client.py
```

Test momentum strategy
```bash
python3 -m tests.backtest_momentum_strategy BTCUSDC
```

Test price change calculation
```bash
python3 -m tests.price_change_backtest
```

Test log momentum signal limits
```bash
python3 -m tests.test_rsi_deviation_signal
```

Test Equity Manager manually:
```bash
/usr/bin/python3 -m modules.equity_manager.equity_manager
```

Test Positions Analyzer manually:
```bash
/usr/bin/python3 -m modules.positions_analyzer.positions_analyzer
```

**Running the tests**

Test Save and Validate:
```bash
/usr/bin/python3 -m pytest -v tests/test_save_and_validate.py
```

##  Tested with

Tested with Tested with Ubuntu 20.04, Python 3.10.18, Pip 25.1.1 and Numby 1.26.4

## Future plans
* More crypto signals:
  * MA Crossover	Buy/Sell	Trend-seuranta
  * MACD	Buy/Sell	Momentum
  * Bollinger	Buy/Sell	Range-breakout
  * Volume Spike	Entry Trigger	Usean muun kanssa
  * Heikin Ashi	Trend Reversal	Visuaalisesti vahva
* When to start buying:
  * When diverge_detector gives buy signal (overrides rsi atleast partly)
  * When rsi_analyzer gives buy signal  
* When to selling:
  * When diverge_detector gives sell signal (overrides rsi atleast partly)
  * When rsi_analyzer gives sell signal 
* Selecting buying or selling method:
  * Market_analyzer
* More Analyzers:
  * VolumeSpikeDetector > Hyvä trigger breakout / breakdown
  * OrderBookAnalyzer > Antaa tarkemman näkemyksen likviditeetistä
  * VolatilityEstimator > Auttaa valitsemaan scalp vs hold
  * TrendStrengthMeter (ADX) > Erottaa aidon trendin huijauksesta
