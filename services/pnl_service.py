from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_pnl_for_symbol(db: Session, symbol: str):
    result = db.execute(
        text("""
            SELECT
                p.symbol,
                p.realized_pnl,
                CASE
                    WHEN pr.latest_price IS NOT NULL
                    THEN p.net_quantity * (pr.latest_price - p.average_cost)
                    ELSE NULL
                END AS unrealized_pnl,
                CASE
                    WHEN pr.latest_price IS NOT NULL
                    THEN p.realized_pnl +
                         (p.net_quantity * (pr.latest_price - p.average_cost))
                    ELSE NULL
                END AS total_pnl
            FROM positions_table p
            LEFT JOIN prices_table pr ON p.symbol = pr.symbol
            WHERE p.symbol = :symbol
        """),
        {"symbol": symbol},
    )
    row = result.fetchone()
    if row is None:
        return None

    return {
        "symbol": row[0],
        "realized_pnl": Decimal(str(row[1])) if row[1] is not None else Decimal("0"),
        "unrealized_pnl": Decimal(str(row[2])) if row[2] is not None else None,
        "total_pnl": Decimal(str(row[3])) if row[3] is not None else None,
    }
