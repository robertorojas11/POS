FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 5000

# Apply migrations, create roles / first admin (idempotent), then serve.
# gthread: each open SSE catalog stream holds a thread, not a whole process.
CMD ["sh", "-c", "FLASK_APP=run.py flask db upgrade -d migrations && python bootstrap.py && exec gunicorn run:app --bind 0.0.0.0:5000 --worker-class gthread --workers 2 --threads 50 --timeout 0"]
