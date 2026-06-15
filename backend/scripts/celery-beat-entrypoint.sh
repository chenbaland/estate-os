#!/bin/sh
set -e

echo "Waiting for backend to be ready..."
until curl -fsS http://backend:8000/health/ >/dev/null 2>&1; do
  sleep 3
done
echo "Backend is ready. Starting Celery beat..."

exec "$@"
