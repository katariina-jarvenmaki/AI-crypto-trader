import os
import json

def check_and_create_path(path):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        except Exception as e:
            print(f"Error creating directory: {e}")

def create_file_if_missing(path):
    if not os.path.exists(path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('')
            print(f"Created empty file: {path}")
        except Exception as e:
            print(f"Error creating file: {e}")

def is_valid_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read()
            if data.strip() == "":
                return True  # Empty file is valid
            json.loads(data)
        return True
    except json.JSONDecodeError:
        return False
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return False

def is_valid_jsonl(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, start=1):
                if line.strip() == "":
                    continue
                json.loads(line)
        return True
    except json.JSONDecodeError as e:
        print(f"JSONL error on line {i}: {e}")
        return False
    except Exception as e:
        print(f"Error in JSONL file: {e}")
        return False

def file_checker(path):
    print(f"Checking file: {path}")

    check_and_create_path(path)
    create_file_if_missing(path)

    if path.endswith('.jsonl'):
        valid = is_valid_jsonl(path)
    else:
        valid = is_valid_json(path)

    if not valid:
        print("File is not valid.")
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('')
            print("File has been emptied.")
        except Exception as e:
            print(f"Error while clearing file: {e}")
        return False

    print("File is ready and valid.")
    return True

# Command-line use
if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser(description="Check and process a JSON/JSONL file.")
    parser.add_argument("path", help="Path to the file (.json or .jsonl)")
    args = parser.parse_args()

    file_checker(args.path)
