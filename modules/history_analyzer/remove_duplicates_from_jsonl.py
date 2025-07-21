import json
import os

def remove_duplicates_from_jsonl(file_path: str):
    print(f"[INFO] Processing file: {file_path}")
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return

    seen = set()
    unique_entries = []
    total_lines = 0
    duplicates_skipped = 0
    parse_errors = 0

    with open(file_path, "r") as f:
        for line in f:
            total_lines += 1
            try:
                entry = json.loads(line.strip())
                key = (entry.get("symbol"), entry.get("timestamp"))
                if key in seen:
                    duplicates_skipped += 1
                    continue
                seen.add(key)
                unique_entries.append(entry)
            except json.JSONDecodeError as e:
                parse_errors += 1
                print(f"[WARN] Failed to parse JSON: {e}")

    with open(file_path, "w") as f:
        for entry in unique_entries:
            f.write(json.dumps(entry) + "\n")

    print(f"[✔] Done. Total lines: {total_lines}")
    print(f"[✔] Unique entries written: {len(unique_entries)}")
    print(f"[✔] Duplicates skipped: {duplicates_skipped}")
    print(f"[✔] JSON parse errors: {parse_errors}")

# Esimerkki kutsusta
if __name__ == "__main__":
    remove_duplicates_from_jsonl("../AI-crypto-trader-logs/analysis-data/history_data_log_day_13_07_2025.jsonl")
