#!/usr/bin/env python3
# balance_manager.py

import json
from datetime import datetime
from integrations.bybit_api_client import client

LOG_FILE = "../AI-crypto-trader-logs/master_balance_log.jsonl"

def fetch_master_equity_info():
    try:
        response = client.get_wallet_balance(accountType="UNIFIED")
        coins = response["result"]["list"][0]["coin"]

        usdt_info = next((coin for coin in coins if coin["coin"] == "USDT"), None)

        if usdt_info:
            total_equity = float(usdt_info.get("equity", 0.0))
            return total_equity

        else:
            print("⚠️ USDT balance not found.")

    except Exception as e:
        print(f"❌ Error fetching master balance: {e}")

    return None

def get_latest_logged_equity(log_path=LOG_FILE):
    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
            if not lines:
                print("⚠️ Log file is empty.")
                return None

            last_entry = json.loads(lines[-1])
            last_equity = float(last_entry["equity"])
            last_timestamp = last_entry["timestamp"]
            return last_equity, last_timestamp

    except FileNotFoundError:
        print(f"⚠️ Log file not found at {log_path}")
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

    return None, None

def compare_equities(current_equity, last_equity):
    if current_equity is None or last_equity is None:
        print("⚠️ Cannot compare equity values — one or both are missing.")
        return None, None, None, None

    difference = current_equity - last_equity
    percent_change = (difference / last_equity * 100) if last_equity != 0 else 0.0

    print("\n📊 Equity Comparison:")
    print(f"A. Current Equity:        {current_equity:.2f} USDT")
    print(f"B. Previous Equity:       {last_equity:.2f} USDT")
    print(f"C. Difference:            {difference:+.2f} USDT")
    print(f"D. Percent Change:        {percent_change:+.2f}%")

    return current_equity, last_equity, difference, percent_change

def calculate_allowed_margin(last_equity, percent=None):
    """
    Laskee sallitun marginaalin tappiollisille long/short-treideille.
    """
    if last_equity is None or last_equity <= 0:
        print("⚠️ Invalid or missing previous equity.")
        return None

    try:
        from modules.equity_manager.config_equity_manager import ALLOWED_TRADE_MARGIN_PERCENT
    except ImportError:
        ALLOWED_TRADE_MARGIN_PERCENT = 25.0  # fallback

    margin_percent = (
        percent if percent is not None
        else ALLOWED_TRADE_MARGIN_PERCENT if ALLOWED_TRADE_MARGIN_PERCENT is not None
        else 25.0
    )

    allowed_amount = (margin_percent / 100.0) * last_equity

    print(f"\n🛡️ Allowed Margin for Negative Trades ({margin_percent:.1f}% of previous equity):")
    print(f"• LONG max loss:  {allowed_amount:.2f} USDT")
    print(f"• SHORT max loss: {allowed_amount:.2f} USDT")

    return {
        "long": allowed_amount,
        "short": allowed_amount,
        "percent": margin_percent
    }

def analyze_equity_status(diff_percent, limit=None):
    """
    Tarkistaa, ylittääkö tappio sallitun prosenttirajan (konfiguroitava).
    
    Args:
        diff_percent (float): Erotus edelliseen equityyn prosentteina (voi olla negatiivinen).
        limit (float, optional): Prosenttiraja tappioille. Jos None, haetaan konfiguraatiosta tai käytetään oletusta (25.0).
    
    Returns:
        dict: Sisältää tiedon onko kaupankäynti estetty ja syy.
    """
    if diff_percent is None:
        return {"block_trades": False, "reason": "Diff percent is undefined"}

    # Hae prosenttiraja konfiguraatiosta, jos mahdollista
    if limit is None:
        try:
            from modules.equity_manager.config_equity_manager import ALLOWED_EQUITY_MARGIN_PERCENT
            limit = float(ALLOWED_EQUITY_MARGIN_PERCENT)
        except (ImportError, AttributeError, ValueError):
            limit = 25.0  # fallback-oletus

    if diff_percent <= -limit:
        return {
            "block_trades": True,
            "reason": f"Equity drop {diff_percent:.2f}% exceeds allowed loss limit (-{limit:.1f}%)"
        }

    return {
        "block_trades": False,
        "reason": f"Equity drop {diff_percent:.2f}% is within safe limits (-{limit:.1f}%)"
    }

def run_equity_manager():
    current_equity = fetch_master_equity_info()
    last_equity, last_ts = get_latest_logged_equity()
    current_equity, last_equity, diff_amount, diff_percent = compare_equities(current_equity, last_equity)
    allowed_negative_margins = calculate_allowed_margin(last_equity)
    status = analyze_equity_status(diff_percent)

    return {
        "current_equity": current_equity,
        "last_equity": last_equity,
        "diff_amount": diff_amount,
        "diff_percent": diff_percent,
        "allowed_negative_margins": allowed_negative_margins,
        "block_trades": status["block_trades"],
        "reason": status["reason"]
    }

if __name__ == "__main__":

    print("\nFetching the current Master Equity...")
    current_equity = fetch_master_equity_info()

    print("\nGetting the previous Equity from the Logs...")
    last_equity, last_ts = get_latest_logged_equity()

    current_equity, last_equity, diff_amount, diff_percent = compare_equities(current_equity, last_equity)

    allowed_negative_margins = calculate_allowed_margin(last_equity)

    print(f"\n✅ Allowed Margin Result: {allowed_negative_margins}")

    status = analyze_equity_status(diff_percent)
    
    print("\n🔒 Trade Status Analysis:")
    print(f"• Block trades: {status['block_trades']}")
    print(f"• Reason:        {status['reason']}")

