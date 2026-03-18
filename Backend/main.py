from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import metrics

app = FastAPI(title="Kaya", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/metrics")
def get_metrics():
    return metrics.collect()


@app.post("/api/shutdown")
def shutdown():
    subprocess.Popen(["sudo", "shutdown", "-h", "now"])
    return {"status": "shutting down"}


@app.post("/api/restart")
def restart():
    subprocess.Popen(["sudo", "shutdown", "-r", "now"])
    return {"status": "restarting"}