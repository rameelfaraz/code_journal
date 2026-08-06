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
    

def detect_outliers_iqr(series: pd.Series) -> int:
    clean = series.dropna()
    if len(clean) < 4:
        return 0
    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return int(((clean < lower) | (clean > upper)).sum())


def has_whitespace_or_casing_issues(series: pd.Series) -> bool:
    clean = series.dropna().astype(str)
    if clean.empty:
        return False

    has_untrimmed = (clean != clean.str.strip()).any()
    has_casing_dupes = clean.str.lower().nunique() < clean.nunique()
    return bool(has_untrimmed or has_casing_dupes)


def build_column_profiles(df: pd.DataFrame) -> list[ColumnProfile]:
    profiles = []
    total_rows = len(df)

    for col in df.columns:
        series = df[col]
        missing_count = int(series.isna().sum())
        missing_percent = round((missing_count / total_rows) * 100, 2) if total_rows > 0 else 0.0
        is_numeric = pd.api.types.is_numeric_dtype(series)

        profiles.append(ColumnProfile(
            name=col,
            dtype=str(series.dtype),
            missing_count=missing_count,
            missing_percent=missing_percent,
            unique_count=int(series.nunique()),
            has_whitespace_issues=has_whitespace_or_casing_issues(series) if not is_numeric else False,
            outlier_count=detect_outliers_iqr(series) if is_numeric else None,
        ))

    return profiles


@app.post("/profile", response_model=ProfileReport, dependencies=[Depends(verify_api_key)])
async def profile_csv(file: UploadFile = File(...), include_outliers: bool = True):
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

    profiles = build_column_profiles(df)

    if not include_outliers:
        for profile in profiles:
            profile.outlier_count = None

    return ProfileReport(
        rows=len(df),
        columns=len(df.columns),
        duplicate_rows=int(df.duplicated().sum()),
        column_names=df.columns.tolist(),
        column_profiles=profiles,
    )
