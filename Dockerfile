FROM python:3.13.2 AS builder

# Environment settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# Set Python path for module resolution
ENV PYTHONPATH=/app

# Install dependencies
RUN python -m venv .venv
COPY requirements.txt ./
RUN .venv/bin/pip install -r requirements.txt

# Copy app code, including the scripts
COPY . .

# Final stage for running the app
FROM python:3.13.2-slim
WORKDIR /app

# Copy the venv and app code from builder
COPY --from=builder /app/.venv .venv/
COPY . .

# ✅ Start the app with Uvicorn
CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
