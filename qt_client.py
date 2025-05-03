import os, time
import requests
from dotenv import load_dotenv, set_key

load_dotenv()

REFRESH_TOKEN = os.getenv("QT_REFRESH_TOKEN")
CLIENT_ID     = os.getenv("QT_CLIENT_ID")
API_SERVER    = None       # will be set after auth
ACCESS_TOKEN  = None
EXPIRES_AT    = 0

def refresh_tokens():
    global ACCESS_TOKEN, API_SERVER, EXPIRES_AT, REFRESH_TOKEN
    print("Refreshing tokens...")
    url = f"https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token={REFRESH_TOKEN}"
    resp = requests.post(url, data={
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID
    })
    resp.raise_for_status()
    data = resp.json()
    ACCESS_TOKEN = data["access_token"]
    REFRESH_TOKEN = data["refresh_token"]  # update for next time
    API_SERVER = data["api_server"]
    EXPIRES_AT = time.time() + data["expires_in"] - 30
    print(f"Tokens refreshed. New expiration time: {EXPIRES_AT}")
    set_key(".env", "QT_REFRESH_TOKEN", REFRESH_TOKEN)

def ensure_token():
    if not ACCESS_TOKEN or time.time() > EXPIRES_AT:
        print("Token expired or missing. Ensuring token...")
        refresh_tokens()
    else:
        print("Token is still valid.")

def api_get(path, params=None):
    print(f"Making GET request to: {path} with params: {params}")
    ensure_token()
    url = f"{API_SERVER}{path}"
    response = requests.get(url, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}, params=params)
    print(f"GET request to {url} completed with status code: {response.status_code}")
    return response.json()

def api_post(path, payload):
    print(f"Making POST request to: {path} with payload: {payload}")
    ensure_token()
    url = f"{API_SERVER}{path}"
    response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"})
    print(f"POST request to {url} completed with status code: {response.status_code}")
    return response.json()

def get_account_id():
    print("Fetching account ID...")
    data = api_get("/v1/accounts")
    account_id = data["accounts"][0]["number"]
    print(f"Account ID fetched: {account_id}")
    return account_id

def find_symbol_id(symbol):
    print(f"Finding symbol ID for: {symbol}")
    data = api_get("/v1/symbols/search", params={"prefix": symbol})
    for s in data["symbols"]:
        if s["symbol"] == symbol:
            symbol_id = s["symbolId"]
            print(f"Symbol ID for {symbol} found: {symbol_id}")
            return symbol_id
    print(f"Symbol {symbol} not found.")
    raise ValueError(f"Symbol {symbol} not found")

def place_order(account_id, order):
    print(f"Placing order for account ID: {account_id} with order details: {order}")
    response = api_post(f"/v1/accounts/{account_id}/orders", { "order": order })
    print(f"Order placed successfully: {response}")
    return response