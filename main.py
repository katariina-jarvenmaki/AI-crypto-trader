# main.py

from modules.pathbuilder.pathbuilder import pathbuilder

def main():

    result = pathbuilder(extension=".json", file_name="multi_ohlcv_fetch", mid_folder="fetch")
    print(f"result: {result}")

if __name__ == "__main__":
    main()