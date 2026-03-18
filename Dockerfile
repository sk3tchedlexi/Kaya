FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    lm-sensors \
    nvme-cli \
    docker.io \
    sudo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/

EXPOSE 9783

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "9783"]