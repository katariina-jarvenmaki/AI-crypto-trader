# modules/master_balance_logger/master_balance_logger.py

import json
from datetime import datetime, timedelta, timezone
import os
import sys

# Lisää projektin juuri polkuun (jotta integraatiot löytyy)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from integrations.bybit_api_client import client

def is_entry_logged_for_today(filepath):
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    today = now.date()

    # Estetään kirjautuminen ennen klo 05:00 UTC
    if now.hour < 5:
        return True  # Aivan kuin merkintä olisi jo olemassa — ei tehdä vielä uutta

    try:
        with open(filepath, "r") as f:
            for line in reversed(f.readlines()):
                try:
                    entry = json.loads(line)
                    if "timestamp" in entry:
                        ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
                        if ts.date() == today:
                            return True
                except (json.JSONDecodeError, ValueError):
                    continue
    except FileNotFoundError:
        return False
    return False

def get_master_account_data():
    try:
        balance_data = client.get_wallet_balance(accountType="UNIFIED")
        equity = float(balance_data['result']['list'][0]['totalEquity'])

        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        since = now - timedelta(hours=24)
        since_ts_ms = int(since.timestamp() * 1000)

        total_pnl = 0.0
        cursor = None

        while True:
            response = client.get_closed_pnl(
                category="linear",
                limit=50,
                startTime=since_ts_ms,
                cursor=cursor
            )
            trades = response["result"]["list"]
            if not trades:
                break

            for trade in trades:
                pnl = float(trade.get("closedPnl", 0.0))
                time_closed = int(trade.get("createdTime", 0))
                if time_closed >= since_ts_ms:
                    total_pnl += pnl

            cursor = response["result"].get("nextPageCursor")
            if not cursor:
                break

        return {
            "timestamp": now.isoformat(),
            "equity": equity,
            "pnl": total_pnl
        }

    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

def append_to_jsonl(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    needs_newline = False
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            f.seek(-1, os.SEEK_END)
            last_char = f.read(1)
            if last_char != b"\n":
                needs_newline = True

    with open(filepath, "a", encoding="utf-8") as f:
        if needs_newline:
            f.write("\n")
        f.write(json.dumps(data) + "\n")
