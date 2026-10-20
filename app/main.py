from fastapi import FastAPI
from app.api.upload import router as upload_router

app = FastAPI(
    title="Datomaly",
    description="Automated Data Quality & Anomaly Detection Platform",
    version="0.1.0"
)

app.include_router(
    upload_router,
    prefix="/api",
    tags=["Datasets"]
)


@app.get("/")
def root():
    return {
        "message": "Datomaly API is running"
    }