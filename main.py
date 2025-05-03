import time
from questrade_client import get_account_id, find_symbol_id, place_order

ACCOUNT = get_account_id()

def open_position(symbol, qty, entry_type="Market"):
    sid = find_symbol_id(symbol)
    order = {
        "symbolId": sid,
        "quantity": qty,
        "isBuy": True,
        "orderType": entry_type,   # "Market" or "Limit"
        # if Limit you'd add "limitPrice": 100.00
        "timeInForce": "GoodTillCancel",
        "clientOrderId": f"entry-{symbol}-{int(time.time())}"
    }
    resp = place_order(ACCOUNT, order)
    return resp["orderId"]

def place_oco_orders(symbol, qty, entry_price):
    stop_price  = round(entry_price * 0.90, 2)
    profit_price= round(entry_price * 1.20, 2)
    sid = find_symbol_id(symbol)
    group_id = f"oco-{symbol}-{int(time.time())}"
    stop_order = {
        "symbolId": sid,
        "quantity": qty,
        "isBuy": False,
        "orderType": "StopLimit",
        "limitPrice": stop_price,
        "stopPrice": stop_price,
        "timeInForce": "GoodTillCancel",
        "clientOrderId": f"{group_id}-stop",
        "orderGroupId": group_id
    }
    profit_order = {
        "symbolId": sid,
        "quantity": qty,
        "isBuy": False,
        "orderType": "Limit",
        "limitPrice": profit_price,
        "timeInForce": "GoodTillCancel",
        "clientOrderId": f"{group_id}-profit",
        "orderGroupId": group_id
    }
    # submit both
    place_order(ACCOUNT, {"symbolId": sid, **stop_order})
    place_order(ACCOUNT, {"symbolId": sid, **profit_order})

def main():
    symbol = "AAPL"
    qty    = 10

    # 1) Open position
    entry_order_id = open_position(symbol, qty)
    print("Entry submitted:", entry_order_id)

    # 2) Poll until filled
    from questrade_client import api_get
    while True:
        status = api_get(f"/v1/accounts/{ACCOUNT}/orders/{entry_order_id}")["orderStatus"]
        print("Waiting on fill...", status)
        if status == "Filled":
            filled = api_get(f"/v1/accounts/{ACCOUNT}/orders/{entry_order_id}")["filledQuantity"]
            avg_price = api_get(f"/v1/accounts/{ACCOUNT}/orders/{entry_order_id}")["averagePrice"]
            print(f"Filled {filled}@{avg_price}")
            # 3) Place OCO orders
            place_oco_orders(symbol, filled, avg_price)
            break
        time.sleep(2)

if __name__ == "__main__":
    main()
