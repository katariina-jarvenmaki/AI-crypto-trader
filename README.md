# AI-crypto-trader
Just a multiplatform AI crypto trader

## Install and Usage

**1. Install libraries**

```bash
pip3 install python-binance pandas pandas_ta ta scipy pybit numpy==1.26.4 matplotlib requests python-dateutil jsonschema 
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
```

**Usage guide**

Run the app
```bash
python3 main.py
```

To run Symbol data fetchers manually (supposted to be ran by cron):
```bash
cd /opt/kjc/int/AI-crypto-trader
/usr/bin/python3 -m modules.symbol_data_fetcher.tasks.potential_trades_checker
/usr/bin/python3 -m modules.symbol_data_fetcher.tasks.fetch_symbols_data
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
/usr/bin/python3 -m modules.pathbuilder.path_selector
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

Test Cron Tasks Prosessor manually:
```bash
/usr/bin/python3 -m core.cron_tasks_processor
```