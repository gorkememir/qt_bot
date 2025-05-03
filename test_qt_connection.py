from qt_client import get_account_id, ensure_token, find_symbol_id

try:
    account_id = get_account_id()
    print(f"Successfully connected to Questrade API. Account ID: {account_id}")
    ensure_token
    find_symbol_id("AAPL")  # Test symbol lookup
except Exception as e:
    print(f"Failed to connect to Questrade API: {e}")