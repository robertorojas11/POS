FROM python:3.11-slim

# Install system dependencies needed for compiling psycopg2 or other C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY . .

# Expose backend port
EXPOSE 5000

# gthread workers: each open SSE catalog stream holds a thread, not a whole process
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5000", "--worker-class", "gthread", "--workers", "2", "--threads", "50", "--timeout", "0"]
