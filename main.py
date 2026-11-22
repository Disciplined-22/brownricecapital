import os
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

app = FastAPI()


@app.get("/")
def read_root():
    # http://localhost:8080 on your host.
    return {
        "message": "Hello, FastAPI!"
    }    