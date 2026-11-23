from fastapi import APIRouter
from services.reconciliation_service import generate_report

router = APIRouter()


@router.post("/reconciliation")
def reconciliation():
    return generate_report()
