# modules/history_archiver/history_archiver.py
# version 2.0, aug 2025

from utils.load_configs_and_logs import load_configs_and_logs

if __name__ == "__main__":

    print(f"\nRunning History Archiver...\n")

    configs_and_logs = load_configs_and_logs([
        {
            "name": "history",
            "mid_folder": "analysis",
            "module_key": "history_analyzer",
            "extension": ".jsonl",
            "return": ["config", "full_log_path", "full_log_schema_path", "logs_path", "log"]
        }
    ])

    history_config = configs_and_logs["history_config"]
    history_log_path = configs_and_logs.get("history_full_log_path")
    history_log_schema_path = configs_and_logs.get("history_full_log_schema_path")
    logs_path = configs_and_logs.get("history_logs_path")
    log = configs_and_logs.get("history_log")
    print(f"history_config: {history_config}")
    print(f"history_log_path: {history_log_path}")
    print(f"history_log_schema_path: {history_log_schema_path}")
    print(f"logs_path: {logs_path}")
    print(f"log: {log}")
