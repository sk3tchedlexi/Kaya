from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import subprocess
import os
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
    # Write to host sysrq-trigger — works from privileged container without systemd
    try:
        with open("/proc/sysrq-trigger", "w") as f:
            f.write("o")
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    return {"status": "shutting down"}


@app.post("/api/restart")
def restart():
    try:
        with open("/proc/sysrq-trigger", "w") as f:
            f.write("b")
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    return {"status": "restarting"}


# Serve frontend static files — works both locally and in Docker
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
if not os.path.isdir(frontend_path):
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")