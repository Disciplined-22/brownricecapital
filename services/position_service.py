from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session


def initialize_position_if_not_exists(db: Session, symbol: str):
    # Insert a position row in positions_table if one does not already exist for the symbol
    # positions_table columns: symbol (PK), net_quantity, average_cost, realized_pnl
    # Uses ON CONFLICT (symbol) DO NOTHING for idempotency since symbol is the primary key
    db.execute(
        text("""
            INSERT INTO positions_table (symbol, net_quantity, average_cost, realized_pnl)
            VALUES (:symbol, 0, 0, 0)
            ON CONFLICT (symbol) DO NOTHING
        """),
        {"symbol": symbol},
    )


def fetch_and_lock_position(db: Session, symbol: str):
    # Lock the position row and fetch its current values in one statement.
    # SELECT ... FOR UPDATE holds the row-level lock until COMMIT or ROLLBACK,
    # preventing concurrent transactions from modifying the same position.
    # Within this same transaction we can still read and update the row.
    result = db.execute(
        text("""
            SELECT net_quantity, average_cost, realized_pnl
            FROM positions_table
            WHERE symbol = :symbol
            FOR UPDATE
        """),
        {"symbol": symbol},
    )
    row = result.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Position not found for {symbol}")
    return {
        "net_quantity": Decimal(str(row[0])),
        "average_cost": Decimal(str(row[1])),
        "realized_pnl": Decimal(str(row[2])),
    }


def check_oversell(side: str, quantity: Decimal, net_quantity: Decimal):
    # Reject SELL orders that would drive net_quantity below zero
    if side == "SELL" and quantity > net_quantity:
        raise HTTPException(
            status_code=400,
            detail="Insufficient position quantity",
        )


def calculate_buy_update(
    net_quantity: Decimal,
    average_cost: Decimal,
    quantity: Decimal,
    price: Decimal,
    realized_pnl: Decimal,
):
    # Weighted average cost method
    # New total cost basis = (old qty × old avg cost) + (buy qty × buy price)
    # New average cost = new total cost basis / new quantity
    new_quantity = net_quantity + quantity
    new_average_cost = (
        (net_quantity * average_cost + quantity * price) / new_quantity
    )
    # realized_pnl unchanged on BUY
    return new_quantity, new_average_cost, realized_pnl


def calculate_sell_update(
    net_quantity: Decimal,
    average_cost: Decimal,
    realized_pnl: Decimal,
    quantity: Decimal,
    price: Decimal,
):
    # average_cost untouched on SELL
    new_quantity = net_quantity - quantity
    # Realized PnL increases by (sell price - average cost) × quantity
    new_realized_pnl = realized_pnl + (price - average_cost) * quantity
    return new_quantity, average_cost, new_realized_pnl


def update_position(
    db: Session,
    symbol: str,
    net_quantity: Decimal,
    average_cost: Decimal,
    realized_pnl: Decimal,
):
    # Persist the recalculated position values back to positions_table
    db.execute(
        text("""
            UPDATE positions_table
            SET net_quantity = :net_quantity,
                average_cost = :average_cost,
                realized_pnl = :realized_pnl
            WHERE symbol = :symbol
        """),
        {
            "symbol": symbol,
            "net_quantity": net_quantity,
            "average_cost": average_cost,
            "realized_pnl": realized_pnl,
        },
    )
