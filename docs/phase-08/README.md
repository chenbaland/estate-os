# Phase 8 — CI/CD Pipeline

**EstateOS Continuous Integration & Deployment**

Automated build, test, and deployment pipelines powered by GitHub Actions. Covers linting, testing, Docker image builds, AWS ECR push, Terraform infrastructure updates, and ECS rolling deployments.

---

## Overview

| Workflow | File | Trigger |
|----------|------|---------|
| CI | `.github/workflows/ci.yml` | Push/PR to `main`, `develop` |
| Deploy | `.github/workflows/deploy.yml` | Push to `main`, manual dispatch |

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Push/PR    │────▶│  CI Pipeline │────▶│  Pass/Fail  │
└─────────────┘     └──────────────┘     └─────────────┘

┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│ Push main   │────▶│ Build+Push   │────▶│ Terraform   │────▶│ ECS Deploy  │
└─────────────┘     │ ECR Images   │     │ Apply       │     │ + CloudFront│
                    └──────────────┘     └─────────────┘     └─────────────┘
```

---

## CI Pipeline (`ci.yml`)

**Trigger:** Push or pull request to `main` or `develop`

**Environment:**

```yaml
PYTHON_VERSION: "3.12"
NODE_VERSION: "20"
```

### Job: `lint-backend`

| Step | Command | Directory |
|------|---------|-----------|
| Install Ruff | `pip install ruff` | `backend/` |
| Lint | `ruff check .` | `backend/` |
| Format check | `ruff format --check .` | `backend/` |

### Job: `test-backend`

**Depends on:** `lint-backend`

**Services:**

| Service | Image | Port |
|---------|-------|------|
| PostgreSQL | `pgvector/pgvector:pg16` | 5432 |
| Redis | `redis:7-alpine` | 6379 |

**Environment:**

```yaml
DJANGO_SETTINGS_MODULE: config.settings.test
SECRET_KEY: test-secret-key
DB_NAME: estateos_test
DB_USER: estateos
DB_PASSWORD: estateos
DB_HOST: localhost
DB_PORT: 5432
REDIS_URL: redis://localhost:6379/0
CELERY_BROKER_URL: memory://
CELERY_RESULT_BACKEND: redis://localhost:6379/1
```

**Steps:**

1. Install pytest, pytest-django, pytest-cov
2. `python manage.py migrate --noinput`
3. `pytest --cov=. --cov-report=xml -v`
4. Upload coverage to Codecov

### Job: `test-frontend`

| Step | Command | Directory |
|------|---------|-----------|
| Install | `npm ci \|\| npm install` | `frontend/` |
| Lint | `npm run lint \|\| true` | `frontend/` |
| Test | `npm test` | `frontend/` |

### Job: `build-docker`

**Depends on:** `test-backend`, `test-frontend`

| Step | Action |
|------|--------|
| Setup Buildx | Docker layer caching via GHA |
| Build backend | `estateos/backend:$GITHUB_SHA` (no push) |
| Build frontend | `estateos/frontend:$GITHUB_SHA` (target: production) |
| Validate compose | `docker compose -f docker-compose.yml config --quiet` |

---

## Deploy Pipeline (`deploy.yml`)

**Trigger:**

- Push to `main` (automatic production deploy)
- Manual `workflow_dispatch` with environment choice (`production` / `staging`)

**Environment:**

```yaml
AWS_REGION: eu-west-1
ECR_BACKEND_REPO: estateos/backend
ECR_FRONTEND_REPO: estateos/frontend
```

### Job: `build-and-push`

Builds and pushes Docker images to Amazon ECR.

| Step | Detail |
|------|--------|
| AWS credentials | `secrets.AWS_ACCESS_KEY_ID`, `secrets.AWS_SECRET_ACCESS_KEY` |
| ECR login | `aws-actions/amazon-ecr-login@v2` |
| Image tag | First 8 chars of `GITHUB_SHA` |
| Backend push | `{registry}/estateos/backend:{tag}` + `:latest` |
| Frontend push | `{registry}/estateos/frontend:{tag}` + `:latest` |
| Cache | GitHub Actions cache (Buildx) |

**Outputs:** `image_tag` → passed to Terraform and ECS jobs

### Job: `terraform`

**Depends on:** `build-and-push`

**Environment:** GitHub environment (`production` or `staging`)

**Working directory:** `infrastructure/terraform/`

| Step | Command |
|------|---------|
| Init | `terraform init` |
| Plan | `terraform plan -var="image_tag={tag}" -var="environment={env}" -out=tfplan` |
| Apply | `terraform apply -auto-approve tfplan` (main branch only) |

**Terraform modules** (see `infrastructure/terraform/`):

| Module | Resources |
|--------|-----------|
| `vpc` | VPC, public/private subnets, NAT gateway |
| `rds` | PostgreSQL 16 Multi-AZ |
| `elasticache` | Redis cluster |
| `amazon_mq` | RabbitMQ broker |
| `opensearch` | Search cluster |
| `ecs` | Fargate services (api, worker, beat, nginx) |
| `alb` | Application Load Balancer |
| `cloudfront` | CDN distribution |
| `s3` | Static/media storage |

### Job: `deploy-ecs`

**Depends on:** `build-and-push`, `terraform`

Forces rolling deployment on all ECS services:

| Service | Cluster | Action |
|---------|---------|--------|
| API | `estateos-{env}-cluster` | `aws ecs update-service --force-new-deployment` |
| Worker | Same | Force new deployment |
| Beat | Same | Force new deployment |
| Nginx | Same | Force new deployment |

**Stability check:**

```bash
aws ecs wait services-stable \
  --cluster estateos-{env}-cluster \
  --services estateos-{env}-api
```

**CloudFront invalidation:**

```bash
aws cloudfront create-invalidation \
  --distribution-id "$DIST_ID" \
  --paths "/*"
```

---

## Required Secrets

Configure in GitHub repository settings → Secrets and variables → Actions:

| Secret | Used By | Description |
|--------|---------|-------------|
| `AWS_ACCESS_KEY_ID` | Deploy | IAM user/role access key |
| `AWS_SECRET_ACCESS_KEY` | Deploy | IAM secret key |

### Recommended IAM Permissions

Deploy role needs:

- `ecr:*` (push images)
- `ecs:UpdateService`, `ecs:DescribeServices`
- `cloudfront:CreateInvalidation`, `cloudfront:ListDistributions`
- Terraform state backend access (S3 + DynamoDB lock)

### GitHub Environments

Create `production` and `staging` environments with:

- Required reviewers (optional, recommended for production)
- Environment-specific secrets if needed
- Deployment branch rules (`main` only for production)

---

## Branch Strategy

| Branch | CI | Deploy |
|--------|-----|--------|
| `main` | Full CI | Auto-deploy to production |
| `develop` | Full CI | — |
| Feature branches | Full CI (via PR) | — |
| Manual dispatch | — | Deploy to staging or production |

### Pull Request Flow

1. Create feature branch from `develop`
2. Push → CI runs lint + tests
3. PR to `develop` → CI must pass
4. Merge to `develop` → CI runs
5. PR `develop` → `main` → CI runs
6. Merge to `main` → Deploy pipeline triggers

---

## Docker Images

### Backend (`backend/Dockerfile`)

- Base: `python:3.12-slim`
- ASGI server: Daphne on port 8000
- Tag pattern: `estateos/backend:{sha}`

### Frontend (`frontend/Dockerfile`)

- Multi-stage build with `production` target
- Next.js standalone output
- Tag pattern: `estateos/frontend:{sha}`

### Local Validation

```bash
# Build images locally (matches CI)
docker build -t estateos/backend:local ./backend
docker build -t estateos/frontend:local --target production ./frontend

# Validate compose
docker compose -f docker-compose.yml config --quiet
docker compose -f docker-compose.yml -f docker-compose.prod.yml config --quiet
```

---

## Rollback Procedure

### ECS Rollback

1. Identify previous working image tag in ECR
2. Update ECS task definition with previous tag
3. Force new deployment:

```bash
aws ecs update-service \
  --cluster estateos-production-cluster \
  --service estateos-production-api \
  --force-new-deployment
```

### Terraform Rollback

```bash
cd infrastructure/terraform
terraform plan -var="image_tag={previous_tag}" -out=rollback.tfplan
terraform apply rollback.tfplan
```

### Database Migrations

Migrations are forward-only. For breaking changes:

1. Deploy backward-compatible code first
2. Run migration
3. Deploy code that uses new schema

Never auto-revert migrations in CI.

---

## Monitoring CI/CD Health

| Signal | Source |
|--------|--------|
| Workflow status | GitHub Actions tab |
| Deploy duration | ECS deployment events |
| Post-deploy health | `GET /health/` smoke check |
| Error spike | Sentry + CloudWatch (see monitoring guide) |

Recommended post-deploy smoke test (manual or scripted):

```bash
curl -f https://api.estateos.app/health/
curl -f https://api.estateos.app/api/schema/
curl -f https://app.estateos.app/
```

---

## Future Enhancements

| Enhancement | Benefit |
|-------------|---------|
| Playwright E2E in CI | Catch UI regressions pre-merge |
| Staging auto-deploy on `develop` | Pre-production validation |
| Blue/green ECS deployments | Zero-downtime with instant rollback |
| Mobile EAS Build in CI | Automated app store builds |
| Dependabot + SAST | Supply chain security |
| Deployment notifications | Slack/PagerDuty on deploy events |

---

## Related Documentation

- [Testing Strategy](../phase-07/README.md)
- [Deployment Guide](../phase-09/deployment-guide.md)
- [Backend Implementation](../phase-04/README.md)
- [Monitoring Guide](../phase-10/monitoring-guide.md)
