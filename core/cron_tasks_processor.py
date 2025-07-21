import subprocess
from pathlib import Path

def cron_tasks_processor():
    """
    Executes all cron-related tasks for OHLCV data processing.
    """
    print("Starting the Cron Tasks Processor...")

    run_price_data_fetcher()

    run_history_analyzer()

def run_price_data_fetcher():
    
    try:
        print("Calling Price Data Fetcher module...")
        subprocess.run(
            ["/usr/bin/python3", "-m", "integrations.price_data_fetcher.price_data_fetcher"],
            check=True
        )
        print("✅ Price Data Fetcher executed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error while executing Price Data Fetcher: {e}")

def run_history_analyzer():
    
    try:
        print("Calling History Analyzer module...")
        subprocess.run(
            ["/usr/bin/python3", "-m", "modules.history_analyzer.history_analyzer"],
            check=True
        )
        print("✅ History Analyzer executed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error while executing History Analyzer: {e}")

def run_balance_logger():
    
    try:
        print("Calling Balance Logger module...")
        subprocess.run(
            ["/usr/bin/python3", "-m", "modules.master_balance_logger.balance_logger"],
            check=True
        )
        print("✅ Balance Logger executed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error while executing Balance Logger: {e}")
