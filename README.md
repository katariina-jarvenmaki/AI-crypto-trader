# AI-crypto-trader
Just a multiplatform AI crypto trader

## Install and Usage

**1. Install libraries**

```bash
pip install ta python-binance pandas_ta scipy
```

**2. Install libraries**

Run the app on default platform (Binance) with default symbol (BTCUSDC) and automatic market state detection
```bash
python3 main.py
```

## Future plans
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