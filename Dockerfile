# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Cloudflared
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    wget \
    && wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb \
    && dpkg -i cloudflared-linux-amd64.deb \
    && rm cloudflared-linux-amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Upgrade pip and install wheel
RUN python -m pip install --upgrade pip && \
    pip install wheel

# Install Python dependencies with verbose output
RUN pip install --no-cache-dir -r requirements.txt --verbose

# Copy the rest of the application
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads && \
    chown -R nobody:nogroup /app/uploads && \
    chmod -R 777 /app/uploads

# Make startup script executable
RUN chmod +x start.sh

# Set environment variables
ENV FLASK_APP=server.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV FLASK_DEBUG=0
ENV GEMINI_API_KEY="AIzaSyD1axXzBXa1p398REp82dMQA0qadmIvafM"
ENV DATABASE_URL="mysql://root:NWLFJLBECpCSADKQeytLVeZDjrDDibZB@crossover.proxy.rlwy.net:15642/railway"

# Switch to non-root user
USER nobody

# Expose ports
EXPOSE 5000
EXPOSE 4040

# Command to run the startup script
CMD ["./start.sh"]
