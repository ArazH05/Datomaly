from fastapi import FastAPI

app = FastAPI(
    title="Datomaly",
    description="Automated Data Quality & Anomaly Detection Platform",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Datomaly API is running"
    }