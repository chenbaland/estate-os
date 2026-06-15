#!/bin/sh
# =============================================================================
# EstateOS Test Environment Entrypoint
# Runs migrations, seeds demo data, creates Django superuser, then starts server
# =============================================================================
set -e

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║         EstateOS Test Environment Starting           ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ---------------------------------------------------------------------------
# Wait for PostgreSQL
# ---------------------------------------------------------------------------
echo "[1/5] Waiting for PostgreSQL..."
until python -c "
import os, sys
try:
    import psycopg2
    psycopg2.connect(
        dbname=os.environ.get('DB_NAME', 'estateos'),
        user=os.environ.get('DB_USER', 'estateos'),
        password=os.environ.get('DB_PASSWORD', 'estateos'),
        host=os.environ.get('DB_HOST', 'postgres'),
        port=os.environ.get('DB_PORT', '5432'),
        connect_timeout=5,
    ).close()
except Exception:
    sys.exit(1)
" 2>/dev/null; do
  printf "."
  sleep 2
done
echo ""
echo "    PostgreSQL is ready."

# ---------------------------------------------------------------------------
# Run migrations
# ---------------------------------------------------------------------------
echo ""
echo "[2/5] Running database migrations..."
python manage.py migrate --noinput
echo "    Migrations complete."

# ---------------------------------------------------------------------------
# Collect static files
# ---------------------------------------------------------------------------
echo ""
echo "[3/5] Collecting static files..."
python manage.py collectstatic --noinput --clear 2>/dev/null || true
echo "    Static files ready."

# ---------------------------------------------------------------------------
# Create Django superuser for admin panel access
# ---------------------------------------------------------------------------
echo ""
echo "[4/5] Creating Django admin superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='djangoadmin@estateos-test.local').exists():
    User.objects.create_superuser(
        username='djangoadmin',
        email='djangoadmin@estateos-test.local',
        password='DjangoAdmin99!',
        first_name='Django',
        last_name='Admin',
    )
    print('    Django admin created: djangoadmin@estateos-test.local / DjangoAdmin99!')
else:
    print('    Django admin already exists.')
"

# ---------------------------------------------------------------------------
# Seed demo data (idempotent — safe to restart)
# ---------------------------------------------------------------------------
echo ""
echo "[5/5] Seeding demo data (2 estates, 12+ users, all modules)..."
python manage.py seed_demo 2>&1 | grep -E "(Created|Skipped|Estate|Error|Warning|TOTAL)" || true
echo ""
echo "    Demo data seeded."

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║               Setup complete — starting server       ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "  Web app:       http://localhost"
echo "  API explorer:  http://localhost/api/docs/"
echo "  Django admin:  http://localhost/admin/"
echo "  Mailpit:       http://localhost:8025"
echo "  RabbitMQ:      http://localhost:15673 (estateos/estateos)"
echo ""
echo "  Demo password for all accounts: DemoPass12345"
echo "  Django admin:  djangoadmin@estateos-test.local / DjangoAdmin99!"
echo ""

exec "$@"
