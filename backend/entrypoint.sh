#!/usr/bin/env sh
set -e

echo "[entrypoint] running database migrations..."
alembic upgrade head

echo "[entrypoint] seeding reference data..."
python -m app.seed

echo "[entrypoint] starting uvicorn on :8000"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "${WEB_CONCURRENCY:-2}" --proxy-headers
