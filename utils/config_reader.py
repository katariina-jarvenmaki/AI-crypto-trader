# modules/load_and_validate/load_and_validate.py
import json
from modules.load_and_validate.load_and_validate import load_and_validate

def config_reader(config_path="config.json", schema_path="modules/load_and_validate/default_schema.json"):
    
    try:
        # Attempt to load and validate
        result = load_and_validate(path=config_path, schema=schema_path)
        return result

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print("❌ " + str(e))
    except Exception as e:
        print(f"❌ Tuntematon virhe: {e}")

if __name__ == "__main__":

    # result = config_reader()
    result = config_reader(
        config_path="../AI-crypto-trader-confs/_TEST/fetch_confs/multi_ohlcv_fetch_config.json", 
        schema_path="../AI-crypto-trader-schemas/_TEST/fetch_schemas/multi_ohlcv_fetch_schema.json"
        )
    print(f"result: {result}")
