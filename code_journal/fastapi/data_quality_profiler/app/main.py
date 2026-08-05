import io
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

app = FastAPI(title="Data Quality & Profiling API")
API_KEY = os.getenv("API_KEY", "")

class ColumnProfile(BaseModel):
    name: str
    dtype: str
    missing_count: int
    missing_percent: float
    unique_count: int
    has_whitespace_issues: bool = False
    outlier_count: int | None = None


class ProfileReport(BaseModel):
    rows: int
    columns: int
    duplicate_rows: int
    column_names: list[str]
    column_profiles: list[ColumnProfile]

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
