import json
import urllib.request

BASE = "http://localhost:8080"


def post_reconciliation():
    """Hit the /reconciliation API and print the report."""
    url = f"{BASE}/reconciliation"
    req = urllib.request.Request(url, method="POST")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
    return data


def main():
    report = post_reconciliation()

    print("Reconciliation Report:")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()