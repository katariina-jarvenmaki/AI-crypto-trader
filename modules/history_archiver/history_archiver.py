# modules/history_archiver/history_archiver.py
# version 2.0, aug 2025

from utils.load_configs_and_logs import load_configs_and_logs
from modules.history_archiver.archive_analysis import archive_analysis
from modules.history_archiver.remove_old_archives import remove_old_archives
from modules.history_archiver.utils import analysis_entries_loader, datetime_manager, get_archive_log_paths, check_if_analysis_log_file_exists

def history_archiver(history_config, history_log_path, log_schema, logs_path):
    """
    Does history archiving and deleting old history archives
    """

    print(f"\nStarting History Archiver...")

    # Config init
    config = history_config["history_archiver"]
    archive_settings = config.get("archive", {"daily": True, "weekly": True, "monthly": True})
    remove_old = config.get("remove_old_archives", True)

    # Load current log entries
    analysis_entries = analysis_entries_loader(config.get("max_age_hours", 1500), history_log_path)

    # Define archive paths & filenames
    datetime_data = datetime_manager(None, config)
    archive_log_paths = get_archive_log_paths(datetime_data, config)

    # ARCHIEVING THE HISTORY ANALYSIS LOGS
    for period in ["daily", "weekly", "monthly"]:
        if not archive_settings.get(period, False):
            continue

        log_path = archive_log_paths[f"{period}_log_path"]
        already_done = check_if_analysis_log_file_exists(log_path)

        if already_done:
            print(f"\n⏭  {period.capitalize()} archiving is already done.")
        else:
            archive_analysis(period, analysis_entries, datetime_data, config, history_log_path, log_path, log_schema)

    # REMOVING OLD ARCHIVES
    if remove_old:
        remove_old_archives(logs_path, config)

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

    history_archiver(
        history_config=history_config,
        history_log_path=history_log_path, 
        log_schema=history_log_schema_path,
        logs_path=logs_path
    )