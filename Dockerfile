FROM python:3.10-slim

WORKDIR /app

# Install system utilities necessary for database builds
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application data
COPY . .

# Set environment
ENV FORWARDED_ALLOW_IPS="*"

# Expose backend service
EXPOSE 8000

# Start Gunicorn server with Uvicorn workers
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "backend.main:app"]
