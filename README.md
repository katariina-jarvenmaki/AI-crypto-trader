# AI-crypto-trader
Just a multiplatform AI crypto trader

## Install and Usage

**1. Install libraries**

```bash
pip3 install python-binance pandas pandas_ta ta scipy pybit numpy==1.26.4 matplotlib requests
```

**2. Make a credentials.py to configs-folder**

Contents:
```bash
# configs/credentials.py

# BINANCE API
BINANCE_API_KEY = 'your_api_key'
BINANCE_API_SECRET = 'your_secret_key'

# BYBIT
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

**Add these Symbol data fetching lines to the cron**
```bash
0 1,5,9,13,17,21 * * * cd /opt/kjc/int/AI-crypto-trader && /usr/bin/python3 -m modules.symbol_data_fetcher.tasks.potential_trades_checker >> logs/cron/temporary_log_potential_trades_checker_cron.log 2>&1
*/15 * * * * cd /opt/kjc/int/AI-crypto-trader && /usr/bin/python3 -m modules.symbol_data_fetcher.tasks.top_symbols_data_fetcher >> logs/cron/temporary_log_top_symbols_data_fetcher_cron.log 2>&1
*/5 * * * * cd /opt/kjc/int/AI-crypto-trader && /usr/bin/python3 -m modules.symbol_data_fetcher.tasks.main_symbols_data_fetcher >> logs/cron/temporary_log_main_symbols_data_fetcher_cron.log 2>&1
```

**Add also these lines to the cron**
```bash
*/5 * * * * cd /opt/kjc/int/AI-crypto-trader && /usr/bin/python3 -m integrations.price_data_fetcher.price_data_fetcher >> logs/cron/temporary_log_price_data_fetcher_cron.log 2>&1
*/5 * * * * cd /opt/kjc/int/AI-crypto-trader && /usr/bin/python3 -m modules.history_analyzer.history_analyzer >> logs/cron/temporary_log_history_analyzer_cron.log 2>&1
```

**Check cron log**
```bash
tail -n 100 /opt/kjc/int/AI-crypto-trader/logs/cron.log
```

**4. Usage guide**

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

Restrict to long-only or short-only (Doesn't affect force the buy / sell or meme trades):
```bash
python3 main.py long-only
python3 main.py short-only
```

To run Symbol data fetchers manually (supposted to be ran by cron):
```bash
cd /opt/kjc/int/AI-crypto-trader
/usr/bin/python3 -m modules.symbol_data_fetcher.tasks.potential_trades_checker
/usr/bin/python3 -m modules.symbol_data_fetcher.tasks.main_symbols_data_fetcher
/usr/bin/python3 -m modules.symbol_data_fetcher.tasks.top_symbols_data_fetcher
```

To run Price Data Fetcher manually (supposted to run with Symbol Data Fetchers):
```bash
/usr/bin/python3 -m integrations.price_data_fetcher.price_data_fetcher
```

To run History analyzer manually  (supposted to run with Symbol Data Fetchers):
```bash
/usr/bin/python3 -m modules.history_analyzer.history_analyzer
```

**4. Testing**

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

Test multi ohlcv handler manually:
```bash
python3 integrations/multi_interval_ohlcv/multi_ohlcv_handler.py
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
