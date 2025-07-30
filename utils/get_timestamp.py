
import pytz
import logging
from datetime import datetime

from modules.load_and_validate.load_and_validate import load_and_validate

general_config = load_and_validate()

def get_timestamp():

    timezone_str = general_config.get("timezone", "UTC")

    try:
        tz = pytz.timezone(timezone_str)
    except Exception as e:
        logging.warning(f"⚠️ Invalid timezone in config: {timezone_str}, defaulting to UTC. Error: {e}")
        tz = pytz.UTC

    timestamp = datetime.now(tz).isoformat()

    return timestamp

if __name__ == "__main__":

    result = get_timestamp()
    print(f"result: {result}")