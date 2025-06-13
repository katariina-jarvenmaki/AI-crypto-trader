# AI-crypto-trader
Just a multiplatform AI crypto trader

## Install and Usage

**1. Install libraries**

```bash
pip install ta python-binance pandas_ta scipy
```

**2. Make a credentials.py to configs-folder**

Contents:
```bash
# configs/credentials.py

# BINANCE API
BINANCE_API_KEY = 'your_api_key'
BINANCE_API_SECRET = 'your_secret_key'

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

Force the long / sell -signal to start longing / selling right away (it does it only for first coinpair and only on first round):
```bash
python3 main.py ETHUSDC long
python3 main.py ETHUSDC sell
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

## Future plans
* More crypto signals:
  * MA Crossover	Buy/Sell	Trend-seuranta
  * MACD	Buy/Sell	Momentum
  * Bollinger	Buy/Sell	Range-breakout
  * Volume Spike	Entry Trigger	Usean muun kanssa
  * Heikin Ashi	Trend Reversal	Visuaalisesti vahva
* When to start longing:
  * When diverge_detector gives long signal (overrides rsi atleast partly)
  * When rsi_analyzer gives long signal  
* When to selling:
  * When diverge_detector gives sell signal (overrides rsi atleast partly)
  * When rsi_analyzer gives sell signal 
* Selecting longing or selling method:
  * Market_analyzer
* More Analyzers:
  * VolumeSpikeDetector > Hyvä trigger breakout / breakdown
  * OrderBookAnalyzer > Antaa tarkemman näkemyksen likviditeetistä
  * VolatilityEstimator > Auttaa valitsemaan scalp vs hold
  * TrendStrengthMeter (ADX) > Erottaa aidon trendin huijauksesta