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

**Testing**

Test Load and Validate manually:
```bash
/usr/bin/python3 -m modules.load_and_validate.load_and_validate
```

Test Path Selector manually:
```bash
/usr/bin/python3 -m utils.path_selector
```

Test Cron Tasks Prosessor manually:
```bash
/usr/bin/python3 -m core.cron_tasks_processor
```

Test Get Filenames manually:
```bash
/usr/bin/python3 -m utils.get_filenames
```

Test multi ohlcv handler manually:
```bash
python3 integrations/multi_interval_ohlcv/multi_ohlcv_handler.py
```
