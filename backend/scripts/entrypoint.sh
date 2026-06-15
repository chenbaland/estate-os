#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until python -c "
import os, sys
import psycopg2
try:
    psycopg2.connect(
        dbname=os.environ.get('DB_NAME', 'estateos'),
        user=os.environ.get('DB_USER', 'estateos'),
        password=os.environ.get('DB_PASSWORD', 'estateos'),
        host=os.environ.get('DB_HOST', 'postgres'),
        port=os.environ.get('DB_PORT', '5432'),
        connect_timeout=5,
    ).close()
except Exception as e:
    sys.exit(1)
" 2>/dev/null; do
  sleep 2
done
echo "PostgreSQL is ready."

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

exec "$@"
