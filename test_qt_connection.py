from qt_client import get_account_id, refresh_tokens

try:
    refresh_tokens()
    account_id = get_account_id()
    print(f"Successfully connected to Questrade API. Account ID: {account_id}")
except Exception as e:
    print(f"Failed to connect to Questrade API: {e}")