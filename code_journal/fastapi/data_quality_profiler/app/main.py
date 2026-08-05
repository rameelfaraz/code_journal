from fastapi import FastAPI

app = FastAPI(title="Data Quality & Profiling API")


@app.get("/")
def root():
    return {"status": "alive"}


@app.get("/health")
def health():
    return {"ok": True}
