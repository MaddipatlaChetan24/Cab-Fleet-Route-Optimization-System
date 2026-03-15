FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app code
COPY main.py .
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Railway dynamically assigns a port. 
# We use the shell form of CMD to ensure $PORT is expanded correctly.
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 4