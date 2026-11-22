from fastapi import APIRouter, HTTPException
from database import SessionLocal
from services.pnl_service import get_pnl_for_symbol

router = APIRouter()


@router.get("/pnl/{symbol}")
def get_pnl_route(symbol: str):
    db = SessionLocal()
    try:
        result = get_pnl_for_symbol(db, symbol)
        if result is None:
            raise HTTPException(status_code=404, detail=f"PnL not found for {symbol}")
        return result
    finally:
        db.close()
