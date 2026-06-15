# Phase 7 — Testing Strategy

**EstateOS Quality Assurance**

Comprehensive testing approach covering unit, integration, end-to-end, load, and security tests across backend, frontend, and mobile surfaces.

---

## Overview

| Layer | Tool | Location |
|-------|------|----------|
| Backend unit/integration | pytest + pytest-django | `backend/*/tests/`, `backend/tests/` |
| Backend coverage | pytest-cov | `backend/pytest.ini` |
| Backend load | Locust | `backend/tests/load/locustfile.py` |
| Backend security | pytest (OWASP markers) | `backend/tests/security/` |
| Frontend lint | ESLint (Next.js config) | `frontend/` |
| Frontend typecheck | TypeScript | `frontend/` |
| CI orchestration | GitHub Actions | `.github/workflows/ci.yml` |

---

## Coverage Targets

| Area | Target | Current Enforcement |
|------|--------|---------------------|
| Backend unit tests | ≥ 80% line coverage | Codecov upload (CI, non-blocking) |
| Backend integration | All critical flows covered | `@pytest.mark.integration` |
| Backend security | Auth, tenant isolation, rate limits | `@pytest.mark.security` |
| Frontend | Lint + typecheck pass | CI `npm run lint`, `tsc` |
| API contract | OpenAPI schema validation | Manual + smoke tests |
| Load | p95 < 500ms at 100 RPS | Locust benchmarks |
| E2E | Top 5 user journeys | Planned (Playwright) |

---

## Backend Tests

### Configuration

`backend/pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
testpaths =
    accounts/tests
    estates/tests
    residents/tests
    visitors/tests
    security/tests
    billing/tests
    payments/tests
    marketplace/tests
    core/tests
    ai/tests
    tests
markers =
    integration: end-to-end integration tests
    security: security and OWASP-related tests
    slow: slow-running tests
```

Fixtures in `backend/conftest.py` provide:

- `user`, `admin_user` — authenticated users with roles
- `estate`, `other_estate` — tenant contexts
- `unit` — resident unit assignment
- `api_client` — DRF test client with auth helpers

### Unit Tests

Each Django app has a `tests/` directory with model, serializer, and view tests.

```bash
cd backend
source .venv/bin/activate

# Run all unit tests
pytest -v

# Run specific app
pytest visitors/tests/ -v

# Run with coverage report
pytest --cov=. --cov-report=html --cov-report=term-missing
open htmlcov/index.html
```

### Integration Tests

Cross-module flows in `backend/tests/integration/test_api_flows.py`:

| Flow | Description |
|------|-------------|
| Resident onboarding → visitor pass → gate scan | Full visitor lifecycle |
| Invoice generation → payment → receipt | Billing pipeline |
| Marketplace order → payment → fulfillment | E-commerce flow |
| Maintenance ticket → assignment → resolution | Operations workflow |

```bash
pytest -m integration -v
```

### Security Tests

`backend/tests/security/test_owasp.py` covers:

| Category | Tests |
|----------|-------|
| Authentication bypass | Unauthenticated access denied, invalid JWT rejected |
| Cross-tenant isolation | Header without membership handled correctly |
| Brute force protection | Repeated failed login attempts throttled |
| Input validation | SQL injection patterns in search rejected |
| Authorization | Role-restricted endpoints enforce permissions |

```bash
pytest -m security -v
```

### Load Tests

Locust scenarios in `backend/tests/load/locustfile.py`:

```bash
cd backend
pip install locust

# Start Locust web UI
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Headless run: 100 users, 10/s spawn rate, 5 minutes
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --headless -u 100 -r 10 -t 5m
```

Simulated endpoints:

- `GET /health/` — baseline latency
- `GET /api/v1/accounts/me/` — authenticated read
- `POST /api/v1/visitors/passes/` — write-heavy pass creation
- `GET /api/v1/analytics/dashboard/` — aggregation query

**Targets:**

| Metric | Threshold |
|--------|-----------|
| p50 latency | < 100ms |
| p95 latency | < 500ms |
| Error rate | < 0.1% |
| Throughput | ≥ 100 RPS sustained |

---

## Frontend Tests

### Current CI Checks

From `.github/workflows/ci.yml`:

```bash
cd frontend
npm ci
npm run lint        # ESLint (non-blocking with || true in CI)
npm test            # Test runner (configure as needed)
npm run typecheck   # tsc --noEmit
```

### Recommended Additions

| Type | Tool | Scope |
|------|------|-------|
| Component unit | Vitest + Testing Library | UI components in `src/components/` |
| Integration | Vitest + MSW | API hook behavior with mocked backend |
| E2E | Playwright | Login, dashboard, visitor pass, billing flows |
| Visual regression | Playwright screenshots | Critical pages dark/light mode |

### E2E Test Plan (Planned)

```
tests/e2e/
├── auth.spec.ts          # Login, logout, session expiry
├── dashboard.spec.ts     # Widget rendering, role filtering
├── visitors.spec.ts      # Create pass, view QR
├── billing.spec.ts       # View invoice, initiate payment
└── marketplace.spec.ts   # Browse, add to cart
```

```bash
# Future command
npx playwright test
npx playwright test --ui
```

---

## Mobile Tests

### Current Checks

```bash
cd mobile
npm run typecheck    # TypeScript validation
npm run lint         # Expo lint
```

### Recommended Additions

| Type | Tool | Scope |
|------|------|-------|
| Component | Jest + RNTL | Button, Input, Card components |
| Navigation | Expo Router testing | Tab switching, deep links |
| E2E | Detox or Maestro | Login, create pass, SOS flow |

---

## Running All Tests Locally

### Prerequisites

Start backing services:

```bash
docker compose up -d postgres redis
```

### Full Backend Suite

```bash
cd backend
export DJANGO_SETTINGS_MODULE=config.settings.test
export DB_NAME=estateos_test DB_USER=estateos DB_PASSWORD=estateos
export DB_HOST=localhost DB_PORT=5432
export REDIS_URL=redis://localhost:6379/0
export CELERY_BROKER_URL=memory://
export SECRET_KEY=test-secret-key

pip install -r requirements.txt -r requirements-dev.txt
python manage.py migrate --noinput
pytest --cov=. --cov-report=term-missing -v
```

### Frontend

```bash
cd frontend
npm ci
npm run lint
npm run typecheck
```

### Mobile

```bash
cd mobile
npm ci
npm run typecheck
npm run lint
```

### Docker Compose Validation

```bash
docker compose -f docker-compose.yml config --quiet
```

---

## CI Pipeline Integration

Tests run automatically on push/PR to `main` and `develop` via `.github/workflows/ci.yml`:

| Job | Depends On | Services |
|-----|------------|----------|
| `lint-backend` | — | — |
| `test-backend` | lint-backend | PostgreSQL (pgvector), Redis |
| `test-frontend` | — | — |
| `build-docker` | test-backend, test-frontend | — |

Backend test environment variables match local test setup (see CI workflow `env` block).

Coverage uploaded to Codecov (non-blocking):

```yaml
- uses: codecov/codecov-action@v4
  with:
    files: backend/coverage.xml
    fail_ci_if_error: false
```

---

## Test Data Management

| Approach | Usage |
|----------|-------|
| Pytest fixtures | Per-test isolated data (`conftest.py`) |
| Factory pattern | Model factories for complex objects (future) |
| `@pytest.mark.django_db` | Database access marker |
| Transaction rollback | Each test runs in a transaction (pytest-django default) |

Never use production data in tests. Test settings (`config.settings.test`) use a separate database (`estateos_test`).

---

## Security Testing Checklist

- [ ] Unauthenticated API access returns 401
- [ ] Invalid/expired JWT returns 401
- [ ] Cross-tenant data access blocked
- [ ] Role-restricted endpoints return 403 for unauthorized roles
- [ ] Login rate limiting activates after N failures
- [ ] SQL injection payloads rejected in search/filter params
- [ ] XSS payloads escaped in API responses
- [ ] CORS restricted to allowed origins in production
- [ ] Payment webhook signatures verified
- [ ] File upload type/size limits enforced

Run: `pytest -m security -v`

---

## Performance Testing Checklist

- [ ] Health endpoint p95 < 50ms
- [ ] Authenticated read p95 < 200ms
- [ ] Write operations p95 < 500ms
- [ ] Dashboard aggregation p95 < 800ms
- [ ] 100 concurrent users sustained for 5 minutes
- [ ] No memory leaks under load (monitor ECS tasks)
- [ ] Celery queue depth stays < 100 under normal load

---

## Related Documentation

- [Backend Implementation](../phase-04/README.md)
- [Frontend Implementation](../phase-05/README.md)
- [CI/CD Pipeline](../phase-08/README.md)
- [Monitoring Guide](../phase-10/monitoring-guide.md)
