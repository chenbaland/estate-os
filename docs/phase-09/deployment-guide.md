# EstateOS Deployment Guide

**Phase 09 — Infrastructure & DevOps**

This guide covers local development with Docker Compose and production deployment to AWS.

---

## Prerequisites

| Tool | Version |
|------|---------|
| Docker | 24+ |
| Docker Compose | 2.20+ |
| Terraform | 1.6+ |
| AWS CLI | 2.x |
| Node.js | 20+ (frontend development) |
| Python | 3.12+ (backend development) |

---

## Local Development

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env with your local settings
```

### 2. Start the full stack

```bash
docker compose up -d
```

This starts:

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL (pgvector) | 5432 | Primary database |
| Redis | 6379 | Cache, sessions, channel layer |
| RabbitMQ | 5672 / 15672 | Celery message broker |
| Elasticsearch | 9200 | Search indexing |
| Backend (Daphne) | 8000 | API + WebSocket |
| Celery Worker | — | Async task processing |
| Celery Beat | — | Scheduled tasks |
| Frontend (Next.js) | 3000 | Web application |
| Nginx | 80 | Reverse proxy |

### 3. Verify services

```bash
# API health check
curl http://localhost/health/

# API documentation
open http://localhost/api/docs/

# RabbitMQ management UI
open http://localhost:15672  # guest/guest
```

### 4. Run migrations manually (if needed)

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

### 5. Stop the stack

```bash
docker compose down          # Stop containers
docker compose down -v       # Stop and remove volumes
```

---

## Production (Docker Compose)

For single-server production deployments:

```bash
cp .env.example .env
# Set production values: SECRET_KEY, DB_PASSWORD, REDIS_PASSWORD, etc.

docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Production overrides include:

- `DEBUG=false` with production Django settings
- No exposed internal service ports
- Restart policies and resource limits
- Prometheus + Grafana monitoring stack
- S3 storage enabled via `USE_S3=true`

---

## AWS Deployment (Terraform)

### Architecture

```
Route 53 → CloudFront → ALB → ECS Fargate
                              ├── Nginx (2+ tasks)
                              ├── API (4+ tasks)
                              ├── Celery Worker (4+ tasks)
                              └── Celery Beat (1 task)
                         RDS PostgreSQL (Multi-AZ)
                         ElastiCache Redis
                         Amazon MQ (RabbitMQ)
                         OpenSearch
                         S3 + CloudFront
```

### 1. Bootstrap Terraform state

Create the S3 bucket and DynamoDB table referenced in `infrastructure/terraform/main.tf`:

```bash
aws s3api create-bucket \
  --bucket estateos-terraform-state \
  --region eu-west-1 \
  --create-bucket-configuration LocationConstraint=eu-west-1

aws dynamodb create-table \
  --table-name estateos-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region eu-west-1
```

### 2. Create ECR repositories

```bash
aws ecr create-repository --repository-name estateos/backend --region eu-west-1
aws ecr create-repository --repository-name estateos/frontend --region eu-west-1
```

### 3. Request ACM certificate

Request a certificate in **us-east-1** (required for CloudFront) and in your deployment region (for ALB):

```bash
aws acm request-certificate \
  --domain-name estateos.app \
  --subject-alternative-names "*.estateos.app" \
  --validation-method DNS \
  --region us-east-1
```

### 4. Apply Terraform

```bash
cd infrastructure/terraform

terraform init
terraform plan \
  -var="certificate_arn=arn:aws:acm:us-east-1:ACCOUNT:certificate/CERT_ID" \
  -var="environment=production"
terraform apply
```

### 5. Configure GitHub Actions secrets

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user/role access key |
| `AWS_SECRET_ACCESS_KEY` | IAM secret key |

The `deploy.yml` workflow automatically:

1. Builds and pushes Docker images to ECR
2. Runs `terraform apply` with the new image tag
3. Forces ECS service redeployment
4. Invalidates CloudFront cache

### 6. Manual deployment

```bash
# Build and push images
docker build -t estateos/backend:latest ./backend
docker tag estateos/backend:latest $ECR_REGISTRY/estateos/backend:latest
docker push $ECR_REGISTRY/estateos/backend:latest

# Force ECS redeployment
aws ecs update-service \
  --cluster estateos-production-cluster \
  --service estateos-production-api \
  --force-new-deployment
```

---

## Environment Variables (Production)

Store sensitive values in AWS Secrets Manager or SSM Parameter Store. Key variables:

| Variable | Source |
|----------|--------|
| `SECRET_KEY` | Secrets Manager |
| `DB_PASSWORD` | RDS (Terraform-generated) |
| `REDIS_URL` | ElastiCache endpoint |
| `CELERY_BROKER_URL` | Amazon MQ endpoint |
| `ELASTICSEARCH_URL` | OpenSearch endpoint |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket (Terraform output) |

---

## Database Operations

### Run migrations in ECS

```bash
aws ecs run-task \
  --cluster estateos-production-cluster \
  --task-definition estateos-production-api \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=DISABLED}" \
  --overrides '{"containerOverrides":[{"name":"api","command":["python","manage.py","migrate","--noinput"]}]}'
```

### Backup verification

RDS automated backups run daily with 35-day retention. Verify in the AWS Console under RDS → Automated backups.

---

## SSL/TLS

- **CloudFront**: ACM certificate (us-east-1)
- **ALB**: ACM certificate (deployment region)
- **Internal**: TLS between ECS tasks and managed services (RDS, ElastiCache, MQ, OpenSearch)

---

## Troubleshooting

| Symptom | Check |
|---------|-------|
| API returns 502 | ECS task health, ALB target group health |
| WebSocket disconnects | Nginx `proxy_read_timeout`, Redis channel layer |
| Celery tasks stuck | RabbitMQ queue depth, worker ECS service count |
| Search not working | OpenSearch cluster health, `ELASTICSEARCH_URL` |
| Static files 404 | S3 bucket policy, CloudFront origin config |

### View logs

```bash
# Local
docker compose logs -f backend celery-worker

# AWS
aws logs tail /ecs/estateos-production/api --follow
```

---

## Related Documentation

- [System Architecture](../phase-02/system-architecture.md)
- [Monitoring Guide](../phase-10/monitoring-guide.md)
