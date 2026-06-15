# Phase 4 — Backend Implementation

**EstateOS Django REST API**

Production-grade multi-tenant backend powering web, mobile, and gate-terminal clients. Built with Django 5, Django REST Framework, PostgreSQL (pgvector), Redis, Celery, and Django Channels.

---

## Overview

| Attribute | Value |
|-----------|-------|
| Framework | Django 5.x + DRF |
| Language | Python 3.12 |
| Database | PostgreSQL 16 with pgvector |
| Cache / Sessions | Redis 7 |
| Task Queue | Celery + RabbitMQ |
| Real-time | Django Channels (Daphne ASGI) |
| Search | Elasticsearch (indexed via Celery) |
| API Docs | drf-spectacular (OpenAPI 3) |

---

## Folder Structure

```
backend/
├── config/                 # Project configuration
│   ├── settings/
│   │   ├── base.py         # Shared settings
│   │   ├── development.py  # Local dev overrides
│   │   ├── production.py   # Production settings
│   │   └── test.py         # CI/test settings
│   ├── urls.py             # Root URL routing
│   ├── asgi.py             # ASGI (HTTP + WebSocket)
│   └── wsgi.py             # WSGI (legacy)
├── core/                   # Cross-cutting concerns
│   ├── middleware/tenant.py  # Multi-tenant X-Estate-Id
│   ├── permissions.py      # Role-based access control
│   ├── pagination.py       # Cursor + page pagination
│   ├── audit.py            # Audit log helpers
│   └── views.py            # Health check endpoint
├── accounts/               # Auth, users, roles, JWT
├── estates/                # Estate (tenant) management
├── residents/              # Resident profiles, units
├── visitors/               # Visitor passes, gate scan, blacklist
├── security/               # Incidents, SOS, patrols
├── billing/                # Invoices, fee schedules
├── payments/               # Payment providers (Stripe, Paystack, Flutterwave)
│   └── providers/
├── utilities/              # Utility accounts, meter readings
├── marketplace/            # Products, orders, vendors
├── pharmacy/               # Prescriptions, medication orders
├── healthcare/             # Appointments, ambulance
├── facilities/             # Amenity booking
├── maintenance/            # Service tickets
├── packages/               # Delivery tracking
├── parking/                # Slots, permits, EV charging
├── community/              # Announcements, polls, groups
├── transportation/         # Rides, shuttle schedules
├── analytics/              # Dashboard metrics, reports
├── ai/                     # AI concierge chat endpoint
├── notifications/          # Push, email, SMS dispatch
├── tests/                  # Cross-module test suites
│   ├── integration/        # End-to-end API flows
│   ├── security/           # OWASP, auth bypass tests
│   └── load/               # Locust load tests
├── scripts/                # Entrypoint, migration helpers
├── conftest.py             # Pytest fixtures (estate, user, api_client)
├── pytest.ini              # Test configuration
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Dev/test dependencies
├── Dockerfile              # Production container
└── manage.py
```

Each domain app follows the standard Django layout:

```
<app>/
├── models.py       # Data models with estate FK (tenant scoping)
├── serializers.py  # DRF serializers with validation
├── views.py        # ViewSets and APIViews
├── urls.py         # App-level URL patterns
├── admin.py        # Django admin registration
├── migrations/     # Database migrations
└── tests/          # App-specific unit tests
```

---

## Architecture Rationale

### Multi-Tenancy via Header Scoping

Every authenticated request includes `X-Estate-Id` header. The `TenantMiddleware` (`core/middleware/tenant.py`) validates membership and attaches `request.estate` for queryset filtering. This approach:

- Keeps a single database with row-level tenant isolation
- Avoids subdomain DNS complexity for mobile clients
- Enables cross-estate admin (super_admin) with explicit estate selection

### Modular Domain Apps

Each business module is a separate Django app with its own models, serializers, and URLs. Benefits:

- Independent testing and deployment of module features
- Clear ownership boundaries for team scaling
- Selective module enablement per estate (enterprise tier)

### JWT Authentication

`rest_framework_simplejwt` provides access/refresh token pairs. Mobile stores tokens in `expo-secure-store`; web uses httpOnly cookies (future) or memory + refresh.

### Async Task Processing

Long-running operations (email, search indexing, payment webhooks, report generation) run via Celery workers. Beat scheduler handles recurring tasks (invoice generation, reminder notifications).

### Payment Provider Abstraction

`payments/providers/base.py` defines a common interface; Stripe, Paystack, and Flutterwave implement region-specific checkout flows. Webhook handlers verify signatures and update invoice status idempotently.

---

## API Surface

Base URL: `/api/v1/`

| Module | Prefix | Key Endpoints |
|--------|--------|---------------|
| Accounts | `/accounts/` | Auth, profile, roles |
| Estates | `/estates/` | CRUD, theme config |
| Residents | `/residents/` | Profiles, units |
| Visitors | `/visitors/` | Passes, scan, logs |
| Security | `/security/` | Incidents, SOS |
| Billing | `/billing/` | Invoices, statements |
| Payments | `/payments/` | Checkout, webhooks |
| Marketplace | `/marketplace/` | Products, orders |
| AI | `/ai/` | Chat completions |
| Analytics | `/analytics/` | Dashboard, reports |

Full specification: [`docs/phase-02/api-specification.md`](../phase-02/api-specification.md)

Interactive docs: `http://localhost:8000/api/docs/` (Swagger UI)

---

## Local Development

### Prerequisites

- Python 3.12+
- PostgreSQL 16 (with pgvector extension)
- Redis 7
- RabbitMQ 3

### Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

cp ../.env.example ../.env
# Configure DB_*, REDIS_URL, CELERY_BROKER_URL

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### With Docker Compose (recommended)

From repository root:

```bash
docker compose up -d
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

Services started: PostgreSQL, Redis, RabbitMQ, Elasticsearch, backend (Daphne), Celery worker, Celery beat.

### Run Tests

```bash
cd backend
pytest -v
pytest -m integration    # Integration tests only
pytest -m security         # Security tests only
pytest --cov=. --cov-report=html
```

### Lint

```bash
ruff check .
ruff format --check .
```

---

## Deployment

### Docker

The production Dockerfile (`backend/Dockerfile`):

- Base: `python:3.12-slim`
- Installs `libpq-dev` for psycopg
- Runs `collectstatic` at build time
- Serves via **Daphne** on port 8000 (ASGI for WebSocket support)

```bash
docker build -t estateos/backend:latest ./backend
docker run -p 8000:8000 --env-file .env estateos/backend:latest
```

### AWS ECS (Production)

Deployed via GitHub Actions (`.github/workflows/deploy.yml`):

1. Build and push image to ECR (`estateos/backend`)
2. Terraform apply updates task definition with new image tag
3. ECS rolling deployment on `estateos-{env}-api` service
4. Separate ECS services for worker and beat

Infrastructure defined in `infrastructure/terraform/`:

| Module | Resource |
|--------|----------|
| `vpc` | VPC, subnets, NAT |
| `rds` | PostgreSQL 16 Multi-AZ |
| `elasticache` | Redis cluster |
| `amazon_mq` | RabbitMQ broker |
| `opensearch` | Elasticsearch-compatible search |
| `ecs` | Fargate services (api, worker, beat, nginx) |
| `alb` | Application Load Balancer + health checks |
| `cloudfront` | CDN for static assets |
| `s3` | Media and static file storage |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL connection |
| `REDIS_URL` | Redis connection string |
| `CELERY_BROKER_URL` | RabbitMQ AMQP URL |
| `USE_S3` | Enable S3 storage (`true` in production) |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket for media |
| `SENTRY_DSN` | Error tracking |
| `STRIPE_SECRET_KEY`, `PAYSTACK_SECRET_KEY` | Payment providers |

See `.env.example` at repository root for the complete list.

### Database Migrations

Migrations run automatically via entrypoint script on container start. For manual runs:

```bash
# Docker Compose
docker compose exec backend python manage.py migrate

# ECS (one-off task)
aws ecs run-task \
  --cluster estateos-production-cluster \
  --task-definition estateos-production-migrate \
  --launch-type FARGATE
```

### Health Checks

| Endpoint | Expected | Used By |
|----------|----------|---------|
| `GET /health/` | `{"status": "ok"}` | ALB, Docker, ECS |
| `GET /api/schema/` | OpenAPI JSON | Smoke tests |

---

## Security

- **RBAC**: Role codes enforced in `core/permissions.py` per ViewSet
- **Tenant isolation**: All querysets filtered by `request.estate`
- **Rate limiting**: Login endpoint throttled (see `tests/security/test_owasp.py`)
- **Audit trail**: Sensitive mutations logged via `core/audit.py`
- **CORS**: Configured for frontend origin in production settings
- **HTTPS**: Terminated at ALB/CloudFront; HSTS enabled

---

## Related Documentation

- [API Specification](../phase-02/api-specification.md)
- [Database Design](../phase-02/database-design.md)
- [System Architecture](../phase-02/system-architecture.md)
- [Deployment Guide](../phase-09/deployment-guide.md)
- [Testing Strategy](../phase-07/README.md)
- [CI/CD Pipeline](../phase-08/README.md)
