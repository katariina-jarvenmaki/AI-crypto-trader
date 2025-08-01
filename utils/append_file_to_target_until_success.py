# utils/append_file_to_target_until_success.py
# version 2.0, aug 2025

import time
from pathlib import Path
from typing import Callable, Optional

def append_file_to_target_until_success(
    temp_path: Path,
    target_path: Path,
    max_retries: int = 5,
    retry_delay: float = 1.0,
    on_success: Optional[Callable[[], None]] = None,
):
    """Appends the contents of a temporary file to a target file, with retries and optional post-success callback."""
    
    if not temp_path.exists():
        print(f"Temp file {temp_path} does not exist, nothing to append.")
        return

    if temp_path.stat().st_size == 0:
        print(f"Temp file {temp_path} is empty, skipping append.")
        return

    for attempt in range(1, max_retries + 1):
        try:
            with open(temp_path, "r") as temp_file:
                temp_lines = temp_file.readlines()

            with open(target_path, "a") as target_file:
                target_file.writelines(temp_lines)

            with open(target_path, "r") as target_file:
                target_lines = target_file.readlines()

            if target_lines[-len(temp_lines):] == temp_lines:
                print(f"✅ Successfully appended {temp_path.name} to {target_path.name} on attempt {attempt}.")
                
                if on_success:
                    on_success()

                break
            else:
                raise IOError("Verification failed: appended lines not found in target file.")

        except Exception as e:
            print(f"Attempt {attempt} failed with error: {e}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("❌ Max retries reached, failed to append file.")
                raise
