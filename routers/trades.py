from fastapi import APIRouter, Body
from services.trade_service import ingest_trade, ingest_trades_from_file

router = APIRouter()


@router.post("/trades")
def ingest_trade_route(trade_data: dict = Body(...)):
    return ingest_trade(trade_data)


@router.post("/trades/load")
def load_trades_route():
    """Load every trade from a JSON file and ingest each one.

    Returns a done summary with per-trade results.
    """
    results = ingest_trades_from_file()
    success = sum(1 for r in results if r["status"] == "success")
    duplicate = sum(1 for r in results if r["status"] == "duplicate")
    error = sum(1 for r in results if r["status"] == "error")

    return {
        "status": "done",
        "trades_processed": len(results),
        "success": success,
        "duplicate": duplicate,
        "error": error,
        "results": results,
    }
