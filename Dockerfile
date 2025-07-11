# Dockerfile
FROM python:3.10-slim

# Install ffmpeg for pydub
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app sources
COPY . .

# Cloud Run listens on $PORT (default 8080)
ENV PORT 8080
EXPOSE 8080

# Run via Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "server:app"]
