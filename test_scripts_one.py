import json
import urllib.request

BASE = "http://localhost:8080"


def post_trades_load():
    """Hit the /trades/load API and print the batch ingestion result."""
    url = f"{BASE}/trades/load"
    req = urllib.request.Request(url, method="POST")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
    return data


if __name__ == "__main__":
    data = post_trades_load()
    print(json.dumps(data, indent=2))
