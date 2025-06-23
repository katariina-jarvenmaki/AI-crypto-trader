# tests/price_change_backtest.py

import pandas as pd
from datetime import datetime, timedelta
import pytz
from riskmanagement.price_change_analyzer import calculate_price_changes, should_block_signal

# Määrittele testattava symboli ja signaali (buy tai sell)
SYMBOL = "BTCUSDC"
SIGNAL = "buy"  # Vaihda "sell" jos haluat testata myyntisignaaleja
INTERVAL_MINUTES = 30  # Kuinka usein testataan (esim. 30 min välein)
LOOKBACK_HOURS = 48     # Takautuva aikaikkuna testaukselle

# HUOM: Käytä tässä testissä UTC-aikaa riippumatta globaalista configista
tz = pytz.utc

# Simuloitu ajanjakso
end_time = datetime.now(tz)
start_time = end_time - timedelta(hours=LOOKBACK_HOURS)

# Iteroi aikaleimoja ja testaa, estettäisiinkö signaali
current_time = start_time
allowed_times = []

print(f"\n🔁 Backtest signal: {SIGNAL.upper()} | Symbol: {SYMBOL} | Period: {LOOKBACK_HOURS}h | TZ: UTC\n")

while current_time <= end_time:
    print(f"\n⏱️ Checking at {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")

    price_changes = calculate_price_changes(SYMBOL, current_time)

    if not should_block_signal(SIGNAL, price_changes):
        print(f"✅ Signal NOT blocked at {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        allowed_times.append(current_time)
    else:
        print(f"🚫 Signal blocked at {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")

    current_time += timedelta(minutes=INTERVAL_MINUTES)

# Tulosta yhteenvedot
print("\n📈 SIGNAL ALLOWED AT THESE TIMES:")
for t in allowed_times:
    print(f"✅ {SIGNAL.upper()} allowed at {t.strftime('%Y-%m-%d %H:%M:%S')} UTC")

print(f"\n🔚 Done. Total allowed signals: {len(allowed_times)}")

