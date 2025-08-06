#!/usr/bin/env python3
# balance_manager.py

import json
from datetime import datetime
from integrations.bybit_api_client import client
from modules.equity_manager.config_equity_manager import LOG_FILE
from modules.equity_manager.equity_stoploss import equity_stoploss
from modules.equity_manager.log_equity_result import log_equity_result

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
            print("⚠️ USDT balance not found in wallet response.")
            print("🔍 Raw response:", json.dumps(response, indent=2))

    except Exception as e:
        print(f"❌ Error fetching master balance: {e}")

    return None

from datetime import datetime, timedelta, timezone

def get_latest_logged_equities(log_path=LOG_FILE):

    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
            if len(lines) < 2:
                print("⚠️ Not enough log entries to compare.")
                return None, None, None

            entries = []
            for line in lines:
                try:
                    data = json.loads(line)
                    ts = datetime.fromisoformat(data["timestamp"])
                    entries.append((ts, data))
                except Exception as e:
                    print(f"⚠️ Skipping invalid log line: {e}")
                    continue

            if len(entries) < 2:
                print("⚠️ Not enough valid log entries.")
                return None, None, None

            # Otetaan viimeisin merkintä ja sen timestamp
            latest_ts = entries[-1][0]

            # Etsitään viimeisin merkintä, joka on vähintään 24h vanha latest_ts:stä
            last_equity = None
            last_ts_24h = None
            for ts, entry in reversed(entries):
                if (latest_ts - ts).total_seconds() >= 24 * 3600:
                    last_equity = entry["current_equity"]
                    last_ts_24h = entry["timestamp"]
                    break

            if last_equity is None:
                print("⚠️ Could not find a log entry at least 24h older than latest entry.")
                # Voidaan halutessa palauttaa viimeisin merkintä ilman ikärajaa:
                last_equity = entries[-1][1]["current_equity"]
                last_ts_24h = entries[-1][1]["timestamp"]

            # Etsitään viimeisin merkintä, joka on vähintään 48h vanha latest_ts:stä
            previous_equity = None
            for ts, entry in reversed(entries):
                if (latest_ts - ts).total_seconds() >= 48 * 3600:
                    previous_equity = entry["current_equity"]
                    break

            if previous_equity is None:
                print("⚠️ Could not find a log entry at least 48h older than latest entry.")

            return last_equity, previous_equity, last_ts_24h

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
        reasons.append(
            f"Equity drop {abs(diff_percent):.2f}% (latest) exceeds allowed loss (-{diff_limit:.1f}%)"
        )

    if prev_percent_change is not None and prev_percent_change <= -prev_limit:
        reasons.append(
            f"Equity drop {abs(prev_percent_change):.2f}% (previous) exceeds allowed loss (-{prev_limit:.1f}%)"
        )

    def label(change):
        return (
            f"equity increase {abs(change):.2f}%"
            if change is not None and change > 0
            else (f"equity drop {abs(change):.2f}%" if change is not None else "N/A")
        )

    if reasons:
        return {
            "block_trades": True,
            "reason": " AND ".join(reasons)
        }

    return {
        "block_trades": False,
        "reason": (
            f"{label(diff_percent)} (latest) and {label(prev_percent_change)} (previous) "
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

    print("\nFetching the current Master Equity...")
    current_equity = fetch_master_equity_info()
    if current_equity is None:
        print("❌ Current equity could not be fetched. Exiting...")
        exit(1)

    print("\nGetting the previous Equity from the Logs...")
    last_equity, previous_equity, last_ts = get_latest_logged_equities("../AI-crypto-trader-logs/analysis-data/equity_manager_log.jsonl")
    if last_equity is None or previous_equity is None:
        print("❌ Cannot continue due to missing log data.")
        exit(1)

    if current_equity is None or last_equity is None or previous_equity is None:
        print("❌ Cannot continue — missing one or more equity values.")
        return {}, {"block_trades": True, "reason": "Missing equity data — cannot evaluate risk."}

    # Continue only if all values are valid
    current_equity, last_equity, difference, percent_change, previous_equity, prev_difference, prev_percent_change = compare_equities(
        current_equity, last_equity, previous_equity, verbose=False
    )
    allowed_negative_margins = calculate_allowed_margin(last_equity, verbose=False)
    status = analyze_equity_status(percent_change, prev_percent_change)
    min_investment_diff = calculate_minimum_investment_diff(current_equity, verbose=False)

    stoploss_info = equity_stoploss()  # haetaan stoploss-tiedot

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
        "min_inv_diff_percent": min_investment_diff["diff_percent"],
        "equity_stoploss": stoploss_info["equity_stoploss"],
        "equity_stoploss_margin": stoploss_info["equity_stoploss_margin"],
        "equity_stoploss_margin_type": stoploss_info["equity_stoploss_margin_type"]
    }

    if status["block_trades"]:
        print("\n⚠️  WARNING: Sudden equity drop detected – trades blocked for safety:")
        print(f"🔒 {status['reason']}")
        print("⏳ Trading will remain blocked. Next equity check will be attempted in 5 minutes.")
        print("🔧 If this is incorrect, update 'master_balance_log.jsonl'. Modify 'config_equity_manager.py' only with strong justification just to be safe.\n")

    log_equity_result(result, {"block_trades": result["block_trades"]})

    return result, status

if __name__ == "__main__":

    print("\nFetching the current Master Equity...")
    current_equity = fetch_master_equity_info()
    if current_equity is None:
        print("❌ Current equity could not be fetched. Exiting...")
        exit(1)

    print("\nGetting the previous Equity from the Logs...")
    last_equity, previous_equity, last_ts = get_latest_logged_equities("../AI-crypto-trader-logs/analysis-data/equity_manager_log.jsonl")
    if last_equity is None or previous_equity is None:
        print("❌ Cannot continue due to missing log data.")
        exit(1)

    current_equity, last_equity, difference, percent_change, previous_equity, prev_difference, prev_percent_change = compare_equities(current_equity, last_equity, previous_equity)

    allowed_negative_margins = calculate_allowed_margin(last_equity)
    min_investment_diff = calculate_minimum_investment_diff(current_equity)
    status = analyze_equity_status(percent_change, prev_percent_change)
    stoploss_info = equity_stoploss()

    print("\n🔒 Trade Status Analysis:")
    print(f"• Block trades:     {status['block_trades']}")
    print(f"• Reason:           {status['reason']}")
    print(f"• Equity Stop Loss: {stoploss_info['equity_stoploss']}%")
    print(f"• Difference:       {stoploss_info['equity_stoploss_margin']}% ({stoploss_info['equity_stoploss_margin_type']})")
    print("")