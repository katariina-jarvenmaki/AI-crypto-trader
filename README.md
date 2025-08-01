# AI-crypto-trader
Just a multiplatform AI crypto trader

## Install and Usage

**1. Install libraries**

```bash
pip3 install python-binance pandas pandas_ta ta scipy pybit numpy==1.26.4 matplotlib requests python-dateutil jsonschema 
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