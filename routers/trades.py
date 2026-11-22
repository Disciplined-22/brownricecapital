from fastapi import APIRouter
from services.trade_service import ingest_trade

router = APIRouter()


@router.post("/trades")
def ingest_trade_route():
    return ingest_trade(None)
