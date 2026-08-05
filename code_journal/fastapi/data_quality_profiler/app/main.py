import io
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

app = FastAPI(title="Data Quality & Profiling API")
API_KEY = os.getenv("API_KEY", "")


@app.get("/")
def root():
    return {"status": "alive"}


def verify_api_key(x_api_key: str = Header(...)) -> None:
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.post("/profile", dependencies=[Depends(verify_api_key)])
async def profile_csv(file: UploadFile = File(...)):
    filename = file.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV has no data")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not parse file as CSV")

    if df.empty:
        raise HTTPException(status_code=400, detail="CSV has no rows")

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "column_names": df.columns.tolist(),
    }
