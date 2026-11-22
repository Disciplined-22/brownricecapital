from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import SessionLocal


def ingest_trade(trade_data=None):
    # --- VALIDATE INPUT ---
    # Validate that required string fields are present after stripping whitespace
    # (venue, trade_id, symbol, side) -> 400 if missing
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

    # Validate that quantity, price, and trade_timestamp are present -> 400 if missing
    if trade_data.get("quantity") is None:
        raise HTTPException(status_code=400, detail="Quantity is required")
    if trade_data.get("price") is None:
        raise HTTPException(status_code=400, detail="Price is required")
    if trade_data.get("trade_timestamp") is None:
        raise HTTPException(status_code=400, detail="Trade timestamp is required")

    quantity = trade_data["quantity"]
    price = trade_data["price"]
    side = trade_data["side"]

    # Validate quantity is finite and > 0 -> 400 otherwise
    if not quantity.is_finite() or quantity <= 0:
        raise HTTPException(400, "Quantity must be positive")

    # Validate price is finite and > 0 -> 400 otherwise
    if not price.is_finite() or price <= 0:
        raise HTTPException(400, "Price must be positive")

    # Validate side is BUY or SELL -> 400 otherwise
    if side not in ("BUY", "SELL"):
        raise HTTPException(400, "Side must be BUY or SELL")

    # --- START TRANSACTION ---
    db: Session = SessionLocal()
    try:
        # --- INSERT TRADE ---
        # Insert the trade with ON CONFLICT (venue, trade_id) DO NOTHING for idempotency
        db.execute(
            text("""
                INSERT INTO trades (venue, trade_id, symbol, side, quantity, price, trade_timestamp)
                VALUES (:venue, :trade_id, :symbol, :side, :quantity, :price, :trade_timestamp)
                ON CONFLICT (venue, trade_id) DO NOTHING
            """),
            {
                "venue": trade_data["venue"],
                "trade_id": trade_data["trade_id"],
                "symbol": trade_data["symbol"],
                "side": trade_data["side"],
                "quantity": quantity,
                "price": price,
                "trade_timestamp": trade_data["trade_timestamp"],
            }
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return {"message": "Trade ingested"}
