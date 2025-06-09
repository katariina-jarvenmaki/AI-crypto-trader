# btcc_api_client.py

import hashlib
import urllib.parse
import requests
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configs.credentials import BTCC_USERNAME, BTCC_PASSWORD, BTCC_API_KEY, BTCC_SECRET_KEY, BTCC_COMPANYID

BTCC_API_URL = "https://api1.btloginc.com:9081"

def btcc_create_signature(params: dict, secret_key: str) -> str:
    sorted_params = sorted(params.items())
    query_string = "&".join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in sorted_params)
    full_string = f"{query_string}&secret_key={secret_key}"
    return hashlib.md5(full_string.encode('utf-8')).hexdigest()

def btcc_login(username, password, api_key, secret_key, company_id=1):
    url = f"{BTCC_API_URL}/v1/user/login"
    params = {
        "user_name": username,
        "password": password,
        "company_id": company_id,
        "api_key": api_key,
    }
    sign = btcc_create_signature(params, secret_key)
    params["sign"] = sign

    response = requests.post(url, data=params)
    return response

# Test BTCC login -> If result is "msg": "API KEY NOT TRADE AUTH", them BTCC doesn't yet support trading through API
def login_and_print():
    response = btcc_login(BTCC_USERNAME, BTCC_PASSWORD, BTCC_API_KEY, BTCC_SECRET_KEY, BTCC_COMPANYID)
    # print("Status code:", response.status_code)
    # print("Response:", response.text)
    data = json.loads(response.text)

    # Check the code
    if data.get("code") == 207:
        print("ERROR: BTCC API-keys on configs/credentials.py aren't up to date")
    elif data.get("code") == 209:
        print("ERROR: API KEY NOT TRADE AUTH - MEANING: BTCC doesn't yet support trading through API")
    else:
        print("BTCC might now support trading through API, so it may be right time to start working on BTCC-integration now!")

if __name__ == "__main__":
    login_and_print()