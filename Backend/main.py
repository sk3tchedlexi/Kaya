from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import metrics

app = FastAPI(title="Kaya", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/metrics")
def get_metrics():
    return metrics.collect()