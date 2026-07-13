FROM python:3.12-slim

# git — commits/push/log; pandoc — docx→markdown conversion
RUN apt-get update && apt-get install -y --no-install-recommends git pandoc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000

# --workers 1: this process is the single writer for the data dir. The
# write_lock in app.py only synchronizes threads within one process, and
# the daily-push background thread must not run more than once — both
# assumptions break under multiple worker processes. Traffic here is a
# handful of internal users, so one worker is not a throughput concern.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "app:app"]
