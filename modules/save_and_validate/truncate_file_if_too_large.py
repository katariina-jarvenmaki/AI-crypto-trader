import os
import time
import logging
from pathlib import Path
from shutil import copyfile

def truncate_file_if_too_large(
    file_path: Path,
    max_size_mb: float = 20.0,
    entries_to_keep: int = 500,
    backup_suffix: str = ".backup",
    log_action: bool = True
):
    """Truncate a text-based file if it exceeds a maximum size.

    Args:
        file_path (Path): Path to the file to be monitored.
        max_size_mb (float): Maximum allowed size in megabytes.
        entries_to_keep (int): Number of last lines to keep.
        backup_suffix (str): Suffix to use in backup filename.
        log_action (bool): Whether to log the action using logging.info.
    """
    if not file_path.exists():
        if log_action:
            logging.info(f"File {file_path} does not exist. Skipping.")
        return

    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb < max_size_mb:
        return

    # Read all lines
    try:
        with file_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        if log_action:
            logging.error(f"Failed to read file {file_path}: {e}")
        return

    lines_to_keep = lines[-entries_to_keep:]

    # Create backup
    timestamp = int(time.time())
    archive_name = file_path.with_name(f"{file_path.stem}_{timestamp}{backup_suffix}{file_path.suffix}")
    try:
        copyfile(file_path, archive_name)
    except Exception as e:
        if log_action:
            logging.error(f"Failed to back up file {file_path}: {e}")
        return

    # Write truncated file
    try:
        with file_path.open("w", encoding="utf-8") as f:
            f.writelines(lines_to_keep)
    except Exception as e:
        if log_action:
            logging.error(f"Failed to write truncated file {file_path}: {e}")
        return

    if log_action:
        logging.info(f"🧹 File {file_path.name} truncated: kept last {len(lines_to_keep)} lines, "
                     f"backup saved to {archive_name.name}")
