#!/usr/bin/env bash
set -euo pipefail

echo "Waiting for Postgres + Redis..."

python - <<'PY'
import os
import time
import socket

import psycopg2

# --- Postgres ---
pg_host = os.getenv("POSTGRES_HOST", "db")
pg_port = int(os.getenv("POSTGRES_PORT", "5432"))
pg_name = os.getenv("POSTGRES_DB")
pg_user = os.getenv("POSTGRES_USER")
pg_password = os.getenv("POSTGRES_PASSWORD")

for _ in range(60):
    try:
        psycopg2.connect(
            host=pg_host,
            port=pg_port,
            dbname=pg_name,
            user=pg_user,
            password=pg_password,
        ).close()
        print("Postgres is up")
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("Postgres is not available")

# --- Redis (TCP connect) ---
rd_host = os.getenv("REDIS_HOST", "redis")
rd_port = int(os.getenv("REDIS_PORT", "6379"))

for _ in range(60):
    try:
        with socket.create_connection((rd_host, rd_port), timeout=1):
            print("Redis is up")
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit("Redis is not available")
PY

echo "Apply migrations..."
python manage.py migrate --noinput

echo "Collect static..."
python manage.py collectstatic --noinput || true

echo "Starting command: $*"
exec "$@"