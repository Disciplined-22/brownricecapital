import os
from dotenv import load_dotenv
from fastapi import FastAPI
from routers import trades
from routers import prices

load_dotenv()

app = FastAPI()

app.include_router(trades.router)
app.include_router(prices.router)


@app.get("/")
def read_root():
    # http://localhost:8080 on your host.
    return {
        "message": "Hello, FastAPI!"
    }


@app.get("/positions")
def get_positions():
    return {"message": "Positions retrieved"}


@app.get("/positions/{symbol}")
def get_position(symbol: str):
    return {"message": f"Position for {symbol}"}


@app.get("/pnl")
def get_pnl_all():
    return {"message": "PnL retrieved"}


@app.get("/pnl/{symbol}")
def get_pnl(symbol: str):
    return {"message": f"PnL for {symbol}"}


@app.post("/reconciliation")
def reconciliation():
    return {"message": "Reconciliation report generated"}    