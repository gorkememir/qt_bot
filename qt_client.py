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
    print("[refresh_tokens] Running: refresh_tokens")
    global ACCESS_TOKEN, API_SERVER, EXPIRES_AT, REFRESH_TOKEN
    print("[refresh_tokens] Refreshing tokens...")
    url = f"https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token={REFRESH_TOKEN}"
    resp = requests.post(url)
    print(f"[refresh_tokens] Token refresh response: {resp.status_code}")
    resp.raise_for_status()
    data = resp.json()
    ACCESS_TOKEN = data["access_token"]
    REFRESH_TOKEN = data["refresh_token"]  # update for next time
    API_SERVER = data["api_server"]
    EXPIRES_AT = time.time() + data["expires_in"] - 30
    print(f"[refresh_tokens] Tokens refreshed. New expiration time: {EXPIRES_AT}")
    print(f"[refresh_tokens] API Server: {API_SERVER}")
    set_key(".env", "QT_REFRESH_TOKEN", REFRESH_TOKEN)

def ensure_token():
    print("[ensure_token] Running: ensure_token")
    if not ACCESS_TOKEN or time.time() > EXPIRES_AT:
        print("[ensure_token] Token expired or missing. Ensuring token...")
        refresh_tokens()
    else:
        print("[ensure_token] Token is still valid.")

def api_get(path, params=None):
    print(f"[api_get] Running: api_get with path={path} and params={params}")
    ensure_token()
    url = f"{API_SERVER}{path}"
    response = requests.get(url, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}, params=params)
    print(f"[api_get] GET request to {url} completed with status code: {response.status_code}")
    return response.json()

def api_post(path, payload):
    print(f"[api_post] Running: api_post with path={path} and payload={payload}")
    ensure_token()
    url = f"{API_SERVER}{path}"
    response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"})
    print(f"[api_post] POST request to {url} completed with status code: {response.status_code}")
    return response.json()

def get_account_id():
    print("[get_account_id] Running: get_account_id")
    print("[get_account_id] Fetching account ID...")
    data = api_get("/v1/accounts")
    account_id = data["accounts"][0]["number"]
    print(f"[get_account_id] Account ID fetched: {account_id}")
    return account_id

def find_symbol_id(symbol):
    print(f"[find_symbol_id] Running: find_symbol_id with symbol={symbol}")
    print(f"[find_symbol_id] Finding symbol ID for: {symbol}")
    data = api_get("/v1/symbols/search", params={"prefix": symbol})
    for s in data["symbols"]:
        if s["symbol"] == symbol:
            symbol_id = s["symbolId"]
            print(f"[find_symbol_id] Symbol ID for {symbol} found: {symbol_id}")
            return symbol_id
    print(f"[find_symbol_id] Symbol {symbol} not found.")
    raise ValueError(f"[find_symbol_id] Symbol {symbol} not found")

def place_order(account_id, order):
    print(f"[place_order] Running: place_order with account_id={account_id} and order={order}")
    print(f"[place_order] Placing order for account ID: {account_id} with order details: {order}")
    response = api_post(f"/v1/accounts/{account_id}/orders", { "order": order })
    print(f"[place_order] Order placed successfully: {response}")
    return response