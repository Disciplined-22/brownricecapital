import json
import urllib.request
from decimal import Decimal


BASE = "http://localhost:8080"


def post(path, data=None):
    """POST helper with JSON body."""
    url = f"{BASE}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def get(path):
    """GET helper."""
    url = f"{BASE}{path}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode())


def main():
    # Step 1: Load trades from trades.json via /trades/load
    print("=== Step 1: Load trades from trades.json ===")
    load_result = post("/trades/load")
    print(json.dumps(load_result, indent=2))

    # Step 2: Set latest price for BTC-USD to 125
    print("\n=== Step 2: Set latest price BTC-USD = 125 ===")
    price_result = post("/prices", {"symbol": "BTC-USD", "price": "125"})
    print(json.dumps(price_result, indent=2))

    # Step 3: Fetch PnL for BTC-USD
    print("\n=== Step 3: Fetch PnL for BTC-USD ===")
    pnl = get("/pnl/BTC-USD")
    print(json.dumps(pnl, indent=2))

    # Step 4: Assert expected values (average cost method)
    print("\n=== Step 4: Assert expected values ===")
    expected_realized_pnl = 75
    expected_unrealized_pnl = 300
    expected_total_pnl = 375


    assert Decimal(str(pnl["realized_pnl"])) == Decimal(str(expected_realized_pnl)), \
        f"realized_pnl: expected {expected_realized_pnl}, got {pnl['realized_pnl']}"

    assert Decimal(str(pnl["unrealized_pnl"])) == Decimal(str(expected_unrealized_pnl)), \
        f"unrealized_pnl: expected {expected_unrealized_pnl}, got {pnl['unrealized_pnl']}"

    assert Decimal(str(pnl["total_pnl"])) == Decimal(str(expected_total_pnl)), \
        f"total_pnl: expected {expected_total_pnl}, got {pnl['total_pnl']}"

    print(f"\nExpected (worked example): net_quantity=15, average_cost=105")
    print("NOTE: /pnl/{symbol} returns realized_pnl, unrealized_pnl, total_pnl only.")
    print("net_quantity and average_cost are stored in positions_table but not exposed by the API.")

    print("\nAll available assertions passed average cost PnL values are correct")


if __name__ == "__main__":
    main()
