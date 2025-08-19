# AI-crypto-trader
Just a multiplatform AI crypto trader

## Install and Usage

**1. Install libraries**

```bash
pip3 install python-binance pandas pandas_ta ta scipy pybit numpy==1.26.4 matplotlib requests python-dateutil jsonschema pytest
```

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

*/1 * * * * cd /opt/kjc/int/AI-crypto-trader && flock -n /tmp/price_data_fetcher.lock -c "/usr/bin/python3 -m integrations.price_data_fetcher.price_data_fetcher >> ../AI-crypto-trader-logs/cron/price_data_fetcher.log 2>&1" || echo "$(date) price_data_fetcher skipped (already running)" >> ../AI-crypto-trader-logs/cron/price_data_fetcher.log

*/1 * * * * cd /opt/kjc/int/AI-crypto-trader && flock -n /tmp/history_data_collector.lock -c "/usr/bin/python3 -m modules.history_data_collector.history_data_collector >> ../AI-crypto-trader-logs/cron/history_data_collector.log 2>&1" || echo "$(date) history_data_collector skipped (already running)" >> ../AI-crypto-trader-logs/cron/history_data_collector.log

*/1 * * * * cd /opt/kjc/int/AI-crypto-trader && flock -n /tmp/history_analyzer.lock -c "/usr/bin/python3 -m modules.history_analyzer.history_analyzer >> ../AI-crypto-trader-logs/cron/history_analyzer.log 2>&1" || echo "$(date) history_analyzer skipped (already running)" >> ../AI-crypto-trader-logs/cron/history_analyzer.log
```

**Usage guide**

Run the app
```bash
python3 main.py
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

**Testing**

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

Test multi ohlcv handler manually:
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

Test History Analyzer manually:
```bash
/usr/bin/python3 -m modules.history_analyzer.history_analyzer
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

**Running the tests**

Test Save and Validate:
```bash
/usr/bin/python3 -m pytest -v tests/test_save_and_validate.py
```