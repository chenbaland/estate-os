# Docker Local Stack

## Prerequisites

Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) (macOS/Windows) or Docker Engine + Compose (Linux).

Verify:
```bash
docker --version
docker compose version
```

## Start Full Stack

```bash
cp .env.example .env
# Edit .env — set JWT_SIGNING_KEY, OAuth keys if needed

docker compose up -d --build
```

## Verify Services

```bash
# All containers running
docker compose ps

# API health
curl http://localhost/health/
# {"status":"ok","service":"estateos-api"}

# API docs
open http://localhost/api/docs/

# Frontend
open http://localhost:3000
```

## Service URLs

| Service | URL |
|---------|-----|
| Nginx (API proxy) | http://localhost |
| Backend (direct) | http://localhost:8000 |
| Frontend | http://localhost:3000 |
| RabbitMQ Management | http://localhost:15672 (guest/guest) |
| Elasticsearch | http://localhost:9200 |

## OAuth Setup (Local)

1. **Google:** Create OAuth 2.0 credentials at [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Redirect URI: `http://localhost:3000/auth/callback`
   - Set `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` in `.env`

2. **Apple:** Register Services ID at [Apple Developer](https://developer.apple.com/account/resources/identifiers/list/serviceId)
   - Set `APPLE_OAUTH_CLIENT_ID`, `APPLE_OAUTH_TEAM_ID`, `APPLE_OAUTH_KEY_ID`, `APPLE_OAUTH_PRIVATE_KEY`

3. Restart backend after updating `.env`:
   ```bash
   docker compose restart backend celery-worker celery-beat
   ```

## API Endpoints (New)

```
POST /api/v1/accounts/auth/register/
POST /api/v1/accounts/auth/token/          # email + password
POST /api/v1/accounts/auth/otp/request/
POST /api/v1/accounts/auth/otp/verify/
GET  /api/v1/accounts/auth/oauth/google/authorize/
POST /api/v1/accounts/auth/oauth/google/callback/
GET  /api/v1/accounts/auth/oauth/apple/authorize/
POST /api/v1/accounts/auth/oauth/apple/callback/
POST /api/v1/visitors/passes/scan/         # gate QR scan
POST /api/v1/billing/invoices/{id}/pay/
POST /api/v1/security/sos-alerts/{id}/acknowledge/
```

All tenant-scoped endpoints require header: `X-Estate-Id: <estate-uuid>`

## Troubleshooting

### Port 5432 already in use (Postgres won't start)

If you see `bind: address already in use` on port 5432, a local PostgreSQL instance is running. EstateOS maps Docker Postgres to **5433** on the host by default in `.env`:

```bash
POSTGRES_PORT=5433
```

Then restart:

```bash
docker compose down && docker compose up -d
```

Containers still talk to `postgres:5432` inside the Docker network — only the host mapping changes.

### Connection refused on port 80

Usually means nginx/backend never started because Postgres failed first. Fix the port conflict above, then:

```bash
docker compose ps          # all services should show "Up"
docker compose up -d       # start any "Created" containers
curl http://localhost/health/
```

```bash
# View logs
docker compose logs -f backend

# Rebuild after code changes
docker compose up -d --build backend

# Reset database
docker compose down -v && docker compose up -d
```
