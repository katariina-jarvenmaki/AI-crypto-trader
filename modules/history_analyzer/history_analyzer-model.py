import matplotlib.pyplot as plt
from datetime import datetime

# 📊 UUSI: Market-tilan päättely

# patch_history_with_market_state("BTCUSDT")
# plot_market_history("BTCUSDT")
# print(get_last_strong_market_state("BTCUSDT"))

def determine_market_state(entry):
    if (
        entry["macd_signal"] == "bullish"
        and entry["flag"] == "bull-flag"
        and entry["change_class"] in ["strong-up", "mild-up"]
        and entry["volume_class"] in ["medium-volume", "high-volume"]
    ):
        return "bull"
    elif (
        entry["macd_signal"] == "bearish"
        and entry["flag"] == "bear-flag"
        and entry["change_class"] in ["strong-down", "mild-down"]
        and entry["volume_class"] in ["medium-volume", "high-volume"]
    ):
        return "bear"
    else:
        return "neutral"

# ✅ Päivitää history-tiedostoon market_state

def patch_history_with_market_state(symbol):
    history = load_history(symbol)
    for entry in history:
        entry["market_state"] = determine_market_state(entry)
    save_history(symbol, history)

# 📈 Visualisointi

def plot_market_history(symbol):
    history = load_history(symbol)
    if not history:
        print(f"Ei dataa symbolille: {symbol}")
        return

    dates = [datetime.fromisoformat(e["timestamp"]) for e in history]
    ema_rsi = [e.get("ema_rsi") for e in history]
    market_state = [e.get("market_state", "neutral") for e in history]

    color_map = {"bull": "green", "bear": "red", "neutral": "gray"}
    state_colors = [color_map.get(state, "gray") for state in market_state]

    plt.figure(figsize=(14, 6))
    plt.title(f"EMA-RSI ja market_state: {symbol}")
    plt.xlabel("Aika")
    plt.ylabel("EMA-RSI")

    plt.plot(dates, ema_rsi, label="EMA-RSI", color="blue")
    plt.scatter(dates, ema_rsi, c=state_colors, label="Market State", s=20)
    plt.legend()
    plt.tight_layout()
    plt.grid(True)
    plt.show()

# ✨ Valinnainen: Hae viimeisin ei-neutral

def get_last_strong_market_state(symbol):
    history = load_history(symbol)
    for entry in reversed(history):
        if entry.get("market_state") in ["bull", "bear"]:
            return entry
    return None
