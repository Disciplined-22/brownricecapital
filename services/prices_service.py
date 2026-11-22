from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.orm import Session


def set_latest_price(db: Session, symbol: str, price: Decimal):
    # Upsert the latest price for a symbol into prices_table
    # prices_table columns: symbol (PK), latest_price, updated_at
    # ON CONFLICT (symbol) DO UPDATE ensures idempotent price updates
    db.execute(
        text("""
            INSERT INTO prices_table (symbol, latest_price, updated_at)
            VALUES (:symbol, :latest_price, NOW())
            ON CONFLICT (symbol) DO UPDATE
            SET latest_price = :latest_price,
                updated_at = NOW()
        """),
        {
            "symbol": symbol,
            "latest_price": price,
        },
    )
