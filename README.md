# AI-crypto-trader
Just a multiplatform AI crypto trader

## Install and Usage

**1. Install libraries**

```bash
pip3 install python-binance pandas pandas_ta ta scipy pybit numpy==1.26.4 matplotlib
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

**3. Usage guide**

Run the app on default platform (Binance) with default coinpair (BTCUSDC) and automatic market state detection
```bash
python3 main.py
```

Run the app on specified platform with default coinpair (BTCUSDC) and automatic market state detection
```bash
python3 main.py binance
```

Run the app on specified coinpair and automatic market state detection
```bash
python3 main.py binance ETHUSDC
python3 main.py binance BTCUSDC ETHUSDC SOLUSDC XRPUSDC ADAUSDC HBARUSDC
```

Force the buy / sell -signal to start buying / selling right away (it does it only for first coinpair and only on first round):
```bash
python3 main.py ETHUSDC buy
python3 main.py ETHUSDC sell
```

Restrict to long-only or short-only (Doesn't accect force the buy / sell):
```bash
python3 main.py ETHUSDC long-only
python3 main.py ETHUSDC short-only
```

Run the market scanner:
```bash
python3 market_scanner.py
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