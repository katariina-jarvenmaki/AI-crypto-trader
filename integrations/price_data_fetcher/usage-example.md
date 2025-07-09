# Price data fetcher

## Usage
```bash
fetcher = ExchangeDataFetcher(
    symbol="ETH-USDT", 
    order=["okx", "binance", "kucoin", "bybit"]
)
data = fetcher.fetch()
print(data)
```