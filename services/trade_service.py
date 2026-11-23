from decimal import Decimal
import json
import os
import sys

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import SessionLocal
import services.position_service as position_service


# ---------------------------------------------------------------------------
# Path setup (matches workers/polling.py)
# ---------------------------------------------------------------------------
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TRADES_FILE = os.getenv("TRADES_FILE", "trades.json")


def _to_decimal(value) -> Decimal:
    return Decimal(str(value))


def ingest_trade(trade_data=None):
    # --- VALIDATE INPUT ---
    if (
        not trade_data
        or not str(trade_data.get("venue", "")).strip()
        or not str(trade_data.get("trade_id", "")).strip()
        or not str(trade_data.get("symbol", "")).strip()
        or not str(trade_data.get("side", "")).strip()
    ):
        raise HTTPException(
            status_code=400,
            detail="Required trade fields are missing"
        )

    if trade_data.get("quantity") is None:
        raise HTTPException(status_code=400, detail="Quantity is required")
    if trade_data.get("price") is None:
        raise HTTPException(status_code=400, detail="Price is required")
    if trade_data.get("timestamp") is None:
        raise HTTPException(status_code=400, detail="Trade timestamp is required")

    quantity = _to_decimal(trade_data["quantity"])
    price = _to_decimal(trade_data["price"])
    side = trade_data["side"]

    if not quantity.is_finite() or quantity <= 0:
        raise HTTPException(400, "Quantity must be positive")

    if not price.is_finite() or price <= 0:
        raise HTTPException(400, "Price must be positive")

    if side not in ("BUY", "SELL"):
        raise HTTPException(400, "Side must be BUY or SELL")

    # --- START TRANSACTION ---
    db: Session = SessionLocal()
    try:
        # --- INSERT TRADE ---
        result = db.execute(
            text("""
                INSERT INTO trades (venue, trade_id, symbol, side, quantity, price, trade_timestamp)
                VALUES (:venue, :trade_id, :symbol, :side, :quantity, :price, :trade_timestamp)
                ON CONFLICT (venue, trade_id) DO NOTHING
            """),
            {
                "venue": trade_data["venue"],
                "trade_id": trade_data["trade_id"],
                "symbol": trade_data["symbol"],
                "side": side,
                "quantity": quantity,
                "price": price,
                "trade_timestamp": trade_data["timestamp"],
            }
        )

        # --- WAS TRADE INSERTED? ---
        if result.rowcount == 0:
            db.commit()
            return {
                "status": "duplicate",
                "message": "Trade already ingested",
                "venue": trade_data["venue"],
                "trade_id": trade_data["trade_id"],
            }

        # Trade was inserted -> proceed to position logic
        # --- INITIALIZE POSITION IF NOT EXISTS ---
        # Insert a position row in positions_table if one does not already exist for the symbol
        # positions_table columns: symbol (PK), net_quantity, average_cost, realized_pnl
        position_service.initialize_position_if_not_exists(db, trade_data["symbol"])

        # --- FETCH AND LOCK POSITION ---
        position = position_service.fetch_and_lock_position(db, trade_data["symbol"])

        # --- CHECK OVERSELL ---
        position_service.check_oversell(side, quantity, position["net_quantity"])

        # --- CALCULATE UPDATES ---
        if side == "BUY":
            new_quantity, new_average_cost, new_realized_pnl = (
                position_service.calculate_buy_update(
                    position["net_quantity"],
                    position["average_cost"],
                    quantity,
                    price,
                    position["realized_pnl"],
                )
            )
        else:  # SELL
            new_quantity, new_average_cost, new_realized_pnl = (
                position_service.calculate_sell_update(
                    position["net_quantity"],
                    position["average_cost"],
                    position["realized_pnl"],
                    quantity,
                    price,
                )
            )

        # --- UPDATE POSITIONS TABLE ---
        position_service.update_position(
            db,
            trade_data["symbol"],
            new_quantity,
            new_average_cost,
            new_realized_pnl,
        )

        db.commit()
        return {"status": "success", "message": "Trade ingested"}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def ingest_trades_from_file(path: str = TRADES_FILE):
    """Load every trade from a JSON file and ingest each one via ingest_trade().

    Returns a list of per-trade result dicts so the caller can report success,
    duplicate, and error counts without aborting the whole batch on a single bad
    row. Re-reading the same file is safe: duplicates are rejected at the
    database level via ON CONFLICT (venue, trade_id) DO NOTHING.
    """
    with open(path, "r") as f:
        trades = json.load(f)

    results = []
    for trade in trades:
        try:
            result = ingest_trade(trade)
            results.append(
                {
                    "trade_id": trade.get("trade_id"),
                    "status": result.get("status"),
                    "message": result.get("message"),
                }
            )
        except Exception as exc:
            results.append(
                {
                    "trade_id": trade.get("trade_id"),
                    "status": "error",
                    "message": str(exc),
                }
            )

    return results
