def empty_the_file(file_path):

    try:
        with open(file_path, 'w') as f:
            f.truncate(0)
        print(f"🧹 File cleaned: {file_path}")

    except Exception as e:
        print(f"❌ Failed to clear the file: {e}")
