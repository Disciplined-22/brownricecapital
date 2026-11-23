# Trade Recorder & PnL Service

A backend service that ingests trades from multiple venues, tracks positions, and reports PnL with idempotency, reconciliation, and oversell checks. Built with Python (FastAPI) and PostgreSQL.

## Setup

1. Create a `.env` file in the project root with your PostgreSQL / Supabase connection string:

```
DATABASE_URL=postgresql+psycopg2://user:password@host:port/dbname
```

2. Ensure Docker is running in the background, then spin up the container:

```
docker-compose -f docker-compose.yml up --build
```

3. Run the assessment test:

```
python test_scripts_2.py
```

4. Optionally run the reconciliation test:

```
python test_reconciliation.py
```

`test_reconciliation.py` compares `trades_reconcile.json` (source of truth) against the data in PostgreSQL/`trades.json` and reports any missing or mismatched trades.

`test_scripts_one.py` is for initial testing only and is not required.

`trades_reconcile.json` is treated as the source of truth. `trades.json` is the data sent to PostgreSQL to simulate a stream of trades to the application.


## Test Scripts

- `test_reconciliation.py` — reconciliation
- `test_scripts_2.py` — assessment test case and for intial run.
- `test_scripts_one.py` — not used (additional lines)