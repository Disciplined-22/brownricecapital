from fastapi import APIRouter, Body
from services.trade_service import ingest_trade

router = APIRouter()


@router.post("/trades")
def ingest_trade_route(trade_data: dict = Body(...)):
    return ingest_trade(trade_data)
