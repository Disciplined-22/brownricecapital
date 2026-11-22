from decimal import Decimal
from fastapi import APIRouter, Body, HTTPException
from database import SessionLocal
from services.prices_service import set_latest_price

router = APIRouter()


@router.post("/prices")
def set_price(price_data: dict = Body(...)):
    symbol = price_data.get("symbol")
    price = price_data.get("price")

    if not symbol or not str(symbol).strip():
        raise HTTPException(status_code=400, detail="Symbol is required")
    if price is None:
        raise HTTPException(status_code=400, detail="Price is required")

    price_decimal = Decimal(str(price))

    db = SessionLocal()
    try:
        set_latest_price(db, symbol, price_decimal)
        db.commit()
        return {"status": "updated", "symbol": symbol, "latest_price": price_decimal}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
