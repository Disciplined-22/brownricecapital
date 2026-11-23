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

3. Run the SQL queries in `db/init.sql` in your IDE (Supabase Postgres SQL editor) to create the `trades`, `positions_table`, and `prices_table` tables. (important)

4. Run the assessment test:

```
python test_scripts_2.py
```

5. Optionally run the reconciliation test:

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


## APIs

| Route | Method | Functionality | Returns |
|-------|--------|---------------|---------|
| `/trades` | POST | Pushes a single trade into PostgreSQL | Trade ingestion status (success/duplicate) |
| `/trades/load` | POST | Batch loads trades from `trades.json` into PostgreSQL | Batch summary: success, duplicate, error counts and per-trade results |
| `/prices` | POST | Sets the latest price for a symbol | Updated status with symbol and latest price |
| `/pnl/{symbol}` | GET | Calculates PnL for a symbol | Realized PnL, unrealized PnL, total PnL |
| `/reconciliation` | POST | Calculates reconciliation report against source of truth | Missing or mismatched trades report |

## Notes

- Reconciliation uses JSON format (`trades_reconcile.json` as source of truth vs `trades.json`) for faster implementation, instead of CSV
- Cost-basis method: Average cost (stated in `DESIGN.md`).

