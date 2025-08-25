# modules/history_archiver/history_archiver.py
# version 2.0, aug 2025

from utils.load_configs_and_logs import load_configs_and_logs
from modules.history_archiver.archive_analysis import archive_analysis
from modules.history_archiver.remove_old_archives import remove_old_archives
from modules.history_archiver.utils import analysis_entries_loader, datetime_manager, get_archive_log_paths, check_if_analysis_log_file_exists

def history_archiver(max_age_hours, history_log_path, log_schema, logs_path):
    """
    Does history archiving and deleting old history archives
    """

    print(f"\nStarting History Archiver...")

    # Load current log entries
    analysis_entries = analysis_entries_loader(max_age_hours, history_log_path)

    # Define archive paths & filenames
    datetime_data = datetime_manager()
    archive_log_paths = get_archive_log_paths(datetime_data)

    # Check archive exisistence
    is_daily_archived = check_if_analysis_log_file_exists(archive_log_paths["daily_log_path"])
    is_weekly_archived = check_if_analysis_log_file_exists(archive_log_paths["weekly_log_path"])
    is_monthly_archived = check_if_analysis_log_file_exists(archive_log_paths["monthly_log_path"])
    if(is_daily_archived == True):
        print("\n⏭  Daily archiving is already done.")
    if(is_weekly_archived == True):
        print("\n⏭  Weekly archiving is already done.")
    if(is_monthly_archived == True):
        print("\n⏭  Monthly archiving is already done.")

    # ARCHIEVING THE HISTORY ANALYSIS LOGS

    # Run the archivers, if there is no existing archive 
    archive_conditions = {
        "daily": (is_daily_archived, archive_log_paths["daily_log_path"]),
        "weekly": (is_weekly_archived, archive_log_paths["weekly_log_path"]),
        "monthly": (is_monthly_archived, archive_log_paths["monthly_log_path"]),
    }

    for period, (is_archived, log_path) in archive_conditions.items():
        if not is_archived:
            archive_analysis(period, analysis_entries, datetime_data, history_log_path, log_path, log_schema)

    # REMOVING OLD ARCHIVES
    remove_old_archives(logs_path)

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
        max_age_hours=1500, 
        history_log_path=history_log_path, 
        log_schema=history_log_schema_path,
        logs_path=logs_path
    )