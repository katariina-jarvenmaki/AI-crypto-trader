import requests

class ExchangeDataFetcher:
    def __init__(self, symbol="BTC-USDT", order=None):
        self.symbol = symbol
        self.exchanges = order or ["okx", "kucoin", "binance", "bybit"]

    def fetch(self):
        for exchange in self.exchanges:
            try:
                method = getattr(self, f"_fetch_from_{exchange}")
                data = method()
                if data:
                    data['source'] = exchange
                    return data
            except Exception as e:
                continue  # try next exchange
        return None

    def _fetch_from_okx(self):
        url = f"https://www.okx.com/api/v5/market/ticker?instId={self.symbol}"
        r = requests.get(url)
        data = r.json()
        if data['code'] == '0':
            t = data['data'][0]
            return {
                "lastPrice": float(t["last"]),
                "priceChangePercent": float(t["chg"]),
                "highPrice": float(t["high24h"]),
                "lowPrice": float(t["low24h"]),
                "volume": float(t["vol24h"]),
                "turnover": float(t["volCcy24h"]),
            }

    def _fetch_from_kucoin(self):
        sym = self.symbol.replace("-", "")
        url = f"https://api.kucoin.com/api/v1/market/stats?symbol={sym}"
        r = requests.get(url)
        data = r.json()
        if data['code'] == '200000':
            t = data['data']
            return {
                "lastPrice": float(t["last"]),
                "priceChangePercent": float(t["changeRate"]) * 100,
                "highPrice": float(t["high"]),
                "lowPrice": float(t["low"]),
                "volume": float(t["vol"]),
                "turnover": float(t["volValue"]),
            }

    def _fetch_from_binance(self):
        sym = self.symbol.replace("-", "").replace("/", "")
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={sym}"
        r = requests.get(url)
        if r.status_code == 200:
            t = r.json()
            return {
                "lastPrice": float(t["lastPrice"]),
                "priceChangePercent": float(t["priceChangePercent"]),
                "highPrice": float(t["highPrice"]),
                "lowPrice": float(t["lowPrice"]),
                "volume": float(t["volume"]),
                "turnover": float(t["quoteVolume"]),
            }

    def _fetch_from_bybit(self):
        sym = self.symbol.replace("-", "")
        url = f"https://api.bybit.com/v2/public/tickers?symbol={sym}"
        r = requests.get(url)
        data = r.json()
        if data['ret_code'] == 0:
            t = data['result'][0]
            return {
                "lastPrice": float(t["last_price"]),
                "priceChangePercent": float(t["price_24h_pcnt"]) * 100,
                "highPrice": float(t["high_price"]),
                "lowPrice": float(t["low_price"]),
                "volume": float(t["volume_24h"]),
                "turnover": float(t["turnover_24h"]),
            }

# Käyttöesimerkki:
if __name__ == "__main__":
    fetcher = ExchangeDataFetcher(symbol="BTC-USDT")  # Voit myös vaihtaa järjestyksen order=["binance", "kucoin", ...]
    data = fetcher.fetch()
    if data:
        print("Löydetyt tiedot:")
        print(data)
    else:
        print("Tietoja ei löytynyt mistään pörssistä.")
