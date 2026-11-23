import json
import os
from decimal import Decimal
from sqlalchemy import text
from database import SessionLocal


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RECONCILE_FILE = os.getenv("RECONCILE_FILE", "trades_reconcile.json")


def _to_decimal(value) -> Decimal:
    return Decimal(str(value))


def load_statement(path: str):
    """Read the venue statement JSON file into a list of trade dicts."""
    with open(path, "r") as f:
        return json.load(f)


def load_db_trades():
    """Query every trade from PostgreSQL into a list of dicts."""
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                SELECT venue, trade_id, symbol, side, quantity, price, trade_timestamp
                FROM trades
            """)
        )
        rows = result.fetchall()
        return [
            {
                "venue": r.venue,
                "trade_id": r.trade_id,
                "symbol": r.symbol,
                "side": r.side,
                "quantity": r.quantity,
                "price": r.price,
                "trade_timestamp": str(r.trade_timestamp),
            }
            for r in rows
        ]
    finally:
        db.close()

#  udnerstand the reconcilation propely 
def generate_report():
    """Compare trades_reconcile.json against the DB trades table.

    Uses Python-side dict comparison keyed by (venue, trade_id).
    Returns a JSON-serialisable report.
    """
    statement_trades = load_statement(RECONCILE_FILE)
    db_trades = load_db_trades()

    # Index both sources by the unique key (venue, trade_id)
    db_index = {(t["venue"], t["trade_id"]): t for t in db_trades}
    stmt_index = {(t["venue"], t["trade_id"]): t for t in statement_trades}

    db_keys = set(db_index)
    stmt_keys = set(stmt_index)

    missing_from_db = [stmt_index[k] for k in stmt_keys - db_keys]

    quantity_mismatch = []
    for k in db_keys & stmt_keys:
        db_t = db_index[k]
        stmt_t = stmt_index[k]

        mismatched_fields = []
        if _to_decimal(db_t["quantity"]) != _to_decimal(stmt_t["quantity"]):
            mismatched_fields.append("quantity")
        if _to_decimal(db_t["price"]) != _to_decimal(stmt_t["price"]):
            mismatched_fields.append("price")
        if db_t["side"] != stmt_t["side"]:
            mismatched_fields.append("side")

        if mismatched_fields:
            quantity_mismatch.append({
                "venue": k[0],
                "trade_id": k[1],
                "symbol": db_t["symbol"],
                "db_quantity": str(db_t["quantity"]),
                "statement_quantity": str(stmt_t["quantity"]),
                "db_price": str(db_t["price"]),
                "statement_price": str(stmt_t["price"]),
                "db_side": db_t["side"],
                "statement_side": stmt_t["side"],
                "mismatched_fields": mismatched_fields,
            })

    return {
        "missing_from_db": missing_from_db,
        "quantity_mismatch": quantity_mismatch,
    }
