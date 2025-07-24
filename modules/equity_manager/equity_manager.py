#!/usr/bin/env python3
# balance_manager.py

import json
from datetime import datetime
from integrations.bybit_api_client import client

LOG_FILE = "../AI-crypto-trader-logs/master_balance_log.jsonl"
MAX_TRADE_MARGIN_PERCENT = 50.0   # This should be at max. 50%
MAX_EQUITY_MARGIN_PERCENT = 25.0  # This should be at max. 25%

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

def get_latest_logged_equities(log_path=LOG_FILE):
    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
            if len(lines) < 2:
                print("⚠️ Not enough log entries to compare.")
                return None, None, None

            last_entry = json.loads(lines[-1])
            previous_entry = json.loads(lines[-2])

            last_equity = float(last_entry["equity"])
            previous_equity = float(previous_entry["equity"])
            last_timestamp = last_entry["timestamp"]

            return last_equity, previous_equity, last_timestamp

    except FileNotFoundError:
        print(f"⚠️ Log file not found at {log_path}")
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

    return None, None, None

def compare_equities(current_equity, last_equity, previous_equity, verbose=True):
    if current_equity is None or last_equity is None:
        if verbose:
            print("⚠️ Cannot compare equity values — one or both are missing.")
            return None, None, None, None, None, None, None

    difference = current_equity - last_equity
    percent_change = (difference / last_equity * 100) if last_equity != 0 else 0.0
    prev_difference = current_equity - previous_equity
    prev_percent_change = (prev_difference / previous_equity * 100) if previous_equity != 0 else 0.0

    if verbose:
        print("\n📊 Equity Comparison:")
        print(f"• Current Equity:            {current_equity:.2f} USDT")
        print(f"• Latest Logged Equity:      {last_equity:.2f} USDT")
        print(f"• Difference (latest):       {difference:+.2f} USDT")
        print(f"• Percent Change (latest):   {percent_change:+.2f}%")
        print(f"• Previous Logged Equity:    {previous_equity:.2f} USDT")
        print(f"• Difference (previous):     {prev_difference:+.2f} USDT")
        print(f"• Percent Change (previous): {prev_percent_change:+.2f}%")

    return current_equity, last_equity, difference, percent_change, previous_equity, prev_difference, prev_percent_change

def calculate_allowed_margin(last_equity, percent=None, verbose=True):
    if last_equity is None or last_equity <= 0:
        if verbose:
            print("⚠️ Invalid or missing previous equity.")
        return None

    try:
        from modules.equity_manager.config_equity_manager import ALLOWED_TRADE_MARGIN_PERCENT
    except ImportError:
        ALLOWED_TRADE_MARGIN_PERCENT = 25.0

    margin_percent = (
        percent if percent is not None
        else ALLOWED_TRADE_MARGIN_PERCENT if ALLOWED_TRADE_MARGIN_PERCENT is not None
        else 25.0
    )

    # Enforce maximum
    if margin_percent > MAX_TRADE_MARGIN_PERCENT:
        if verbose:
            print(f"⚠️ Trade margin percent {margin_percent}% exceeds max allowed ({MAX_TRADE_MARGIN_PERCENT}%) — using max.")
        margin_percent = MAX_TRADE_MARGIN_PERCENT

    allowed_amount = (margin_percent / 100.0) * last_equity

    if verbose:
        print(f"\n🛡️ Allowed Margin for Negative Trades ({margin_percent:.1f}% of previous equity):")
        print(f"• LONG max loss:  {allowed_amount:.2f} USDT")
        print(f"• SHORT max loss: {allowed_amount:.2f} USDT")

    return {
        "long": allowed_amount,
        "short": allowed_amount,
        "percent": margin_percent
    }

def analyze_equity_status(diff_percent, prev_percent_change, limit=None):
    """
    Tarkistaa, ylittääkö tappio diff_percent TAI prev_percent_change osalta
    sallitun prosenttirajan (konfiguroitava kummallekin).
    
    Args:
        diff_percent (float): Erotus edelliseen equityyn prosentteina (voi olla negatiivinen).
        prev_percent_change (float): Erotus toissimpaan equityyn prosentteina.
        limit (float, optional): Yleinen fallback-prosenttiraja, jos konfiguraatio puuttuu.
    
    Returns:
        dict: Sisältää tiedon onko kaupankäynti estetty ja syy.
    """
    if diff_percent is None and prev_percent_change is None:
        return {"block_trades": False, "reason": "Both diff percent values are undefined"}

    # Aseta oletusraja
    fallback_limit = limit if limit is not None else 25.0

    try:
        from modules.equity_manager.config_equity_manager import (
            ALLOWED_EQUITY_MARGIN_PERCENT,
            ALLOWED_PREV_EQUITY_MARGIN_PERCENT,
        )
        diff_limit = float(ALLOWED_EQUITY_MARGIN_PERCENT)
        prev_limit = float(ALLOWED_PREV_EQUITY_MARGIN_PERCENT)
    except (ImportError, AttributeError, ValueError):
        diff_limit = fallback_limit
        prev_limit = fallback_limit

    reasons = []

    if diff_percent is not None and diff_percent <= -diff_limit:
        reasons.append(f"Equity drop {diff_percent:.2f}% (latest) exceeds allowed loss (-{diff_limit:.1f}%)")

    if prev_percent_change is not None and prev_percent_change <= -prev_limit:
        reasons.append(f"Equity drop {prev_percent_change:.2f}% (previous) exceeds allowed loss (-{prev_limit:.1f}%)")

    if reasons:
        return {
            "block_trades": True,
            "reason": " OR ".join(reasons)
        }

    return {
        "block_trades": False,
        "reason": (
            f"Equity drop {diff_percent:.2f}% (latest) and {prev_percent_change:.2f}% (previous) "
            f"are within safe limits (-{diff_limit:.1f}% / -{prev_limit:.1f}%)"
        )
    }

def calculate_minimum_investment_diff(current_equity, verbose=True):

    from modules.equity_manager.config_equity_manager import COPYTRADE_MINIMUM_INVESTMENT

    diff_amount = current_equity - COPYTRADE_MINIMUM_INVESTMENT
    if COPYTRADE_MINIMUM_INVESTMENT == 0:
        diff_percent = 0.0
    else:
        diff_percent = (diff_amount / COPYTRADE_MINIMUM_INVESTMENT) * 100

    if verbose:
        print("\n💰 Minimum Investment Check:")
        print(f"• Current Equity:     {current_equity} USDT")
        print(f"• Minimum Investment: {COPYTRADE_MINIMUM_INVESTMENT} USDT")
        print(f"• Difference Amount:  {diff_amount:.2f} USDT")
        print(f"• Difference Percent: {diff_percent:.2f} %")

    return {
        "minimum_investment": COPYTRADE_MINIMUM_INVESTMENT,
        "diff_amount": diff_amount,
        "diff_percent": diff_percent
    }

def run_equity_manager():
    current_equity = fetch_master_equity_info()
    last_equity, previous_equity, last_ts = get_latest_logged_equities()
    current_equity, last_equity, difference, percent_change, previous_equity, prev_difference, prev_percent_change = compare_equities(current_equity, last_equity, previous_equity, verbose=False)
    allowed_negative_margins = calculate_allowed_margin(last_equity, verbose=False)
    status = analyze_equity_status(percent_change, prev_percent_change)
    min_investment_diff = calculate_minimum_investment_diff(current_equity, verbose=False)

    result = {
        "current_equity": current_equity,
        "last_equity": last_equity,
        "diff_amount": difference,
        "diff_percent": percent_change,
        "previous_equity": previous_equity,
        "prev_diff_amount": prev_difference,
        "prev_diff_percent": prev_percent_change,
        "allowed_negative_margins": allowed_negative_margins,
        "block_trades": status["block_trades"],
        "reason": status["reason"],
        "minimum_investment": min_investment_diff["minimum_investment"],
        "min_inv_diff_amount": min_investment_diff["diff_amount"],
        "min_inv_diff_percent": min_investment_diff["diff_percent"]
    }

    if status["block_trades"]:
        print("\n⚠️  WARNING: Sudden equity drop detected – trades blocked for safety:")
        print(f"🔒 {status['reason']}")
        print("⏳ Trading will remain blocked. Next equity check will be attempted in 5 minutes.")
        print("🔧 If this is incorrect, update 'master_balance_log.jsonl'. Modify 'config_equity_manager.py' only with strong justification just to be safe.\n")

    return result

if __name__ == "__main__":

    print("\nFetching the current Master Equity...")
    current_equity = fetch_master_equity_info()

    print("\nGetting the previous Equity from the Logs...")
    last_equity, previous_equity, last_ts = get_latest_logged_equities()

    current_equity, last_equity, difference, percent_change, previous_equity, prev_difference, prev_percent_change = compare_equities(current_equity, last_equity, previous_equity)

    allowed_negative_margins = calculate_allowed_margin(last_equity)

    min_investment_diff = calculate_minimum_investment_diff(current_equity)

    status = analyze_equity_status(percent_change, prev_percent_change)
    
    print("\n🔒 Trade Status Analysis:")
    print(f"• Block trades: {status['block_trades']}")
    print(f"• Reason:       {status['reason']}")