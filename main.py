import os
from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import text
from database import SessionLocal
from routers import trades
from routers import prices
from routers import pnl
from routers import reconciliation

load_dotenv()

app = FastAPI()

app.include_router(trades.router)
app.include_router(prices.router)
app.include_router(pnl.router)
app.include_router(reconciliation.router)


@app.get("/")
def read_root():
    # http://localhost:8080 on your host.
    health_status = health()
    return {
        "message": "Hello, FastAPI!",
        "health": health_status,
    }


@app.get("/health")
def health():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "degraded", "database": "disconnected", "error": str(e)}
    finally:
        db.close()