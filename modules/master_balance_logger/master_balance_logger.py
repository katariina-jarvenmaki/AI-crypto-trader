import argparse
import os
from datetime import datetime
from modules.master_balance_logger.log_master_account import get_master_account_data, append_to_jsonl, is_entry_logged_for_today

# 🔧 Logitiedosto (täydellinen polku)
LOG_FILE = "../AI-crypto-trader-logs/master_balance_log.jsonl"

def main():
    if is_entry_logged_for_today(LOG_FILE):
        print("⏩ Merkintä tälle päivälle on jo olemassa. Ei kirjata uudestaan.")
        return

    data = get_master_account_data()
    append_to_jsonl(data, LOG_FILE)
    print(f"✅ Kirjattu: {data['timestamp']} | Equity: {data.get('equity')} | PNL 24h: {data.get('pnl')}")

if __name__ == "__main__":
    main()