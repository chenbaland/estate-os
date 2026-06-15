# EstateOS Monitoring Guide

**Phase 10 — Observability & Monitoring**

This guide covers metrics collection, dashboards, alerting, and log management for EstateOS.

---

## Overview

| Tool | Purpose | Environment |
|------|---------|-------------|
| Prometheus | Metrics collection and storage | Local (compose prod), self-hosted |
| Grafana | Dashboards and visualization | Local (compose prod) |
| CloudWatch | AWS infrastructure metrics and logs | Production (AWS) |
| Sentry | Error tracking | All environments (configure separately) |

---

## Local Monitoring Stack

Start Prometheus and Grafana with the production compose overlay:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d prometheus grafana
```

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| Grafana | http://localhost:3001 | admin / (set `GRAFANA_ADMIN_PASSWORD`) |
| Prometheus | http://localhost:9090 | — |

### Pre-provisioned dashboard

The **EstateOS Overview** dashboard (`monitoring/grafana/dashboards/estateos-overview.json`) includes:

- API request rate and p95 latency
- Celery queue depth
- Redis connections and memory
- PostgreSQL active connections
- Service health indicators (API, Redis, RabbitMQ, Elasticsearch)

---

## Prometheus Configuration

Configuration file: `monitoring/prometheus/prometheus.yml`

### Scrape targets

| Job | Target | Metrics |
|-----|--------|---------|
| `estateos-backend` | `backend:8000/metrics` | Django HTTP metrics |
| `estateos-nginx` | `nginx:80` | Nginx stub status |
| `postgres` | `postgres-exporter:9187` | DB connections, query stats |
| `redis` | `redis-exporter:9121` | Memory, clients, ops/sec |
| `rabbitmq` | `rabbitmq:15692` | Queue depth, message rates |
| `elasticsearch` | `elasticsearch:9200` | Cluster health, indexing rate |
| `celery` | `celery-exporter:9808` | Task throughput, failures |

> **Note:** Exporter sidecars (postgres-exporter, redis-exporter, celery-exporter) are referenced in the Prometheus config but not included in the base compose file. Add them when enabling full observability locally.

### Adding Django Prometheus metrics

Install `django-prometheus` in the backend and add to `INSTALLED_APPS` and `MIDDLEWARE` to expose `/metrics` endpoint. Until then, the `up` probe and health endpoint provide basic availability monitoring.

---

## Grafana Setup

### Datasources

Auto-provisioned via `monitoring/grafana/provisioning/datasources.yml`:

- **Prometheus** (default) — `http://prometheus:9090`
- **CloudWatch** — for production AWS metrics (requires IAM credentials)

### Dashboard provisioning

Dashboards are loaded from `monitoring/grafana/dashboards/` via `monitoring/grafana/provisioning/dashboards.yml`.

To add a custom dashboard:

1. Create or export a JSON dashboard file in `monitoring/grafana/dashboards/`
2. Restart Grafana: `docker compose restart grafana`

---

## Production Monitoring (AWS)

### CloudWatch metrics (automatic)

ECS Container Insights provides:

- CPU and memory utilization per service
- Running task count
- Network I/O

RDS, ElastiCache, Amazon MQ, and OpenSearch emit metrics automatically.

### Key CloudWatch alarms

| Alarm | Metric | Threshold | Action |
|-------|--------|-----------|--------|
| API High CPU | `ECSServiceAverageCPUUtilization` | > 80% for 5 min | Scale out |
| API Unhealthy | `UnHealthyHostCount` (ALB) | > 0 for 2 min | PagerDuty |
| RDS Storage | `FreeStorageSpace` | < 10 GB | Email alert |
| Redis Memory | `DatabaseMemoryUsagePercentage` | > 80% | Scale up |
| MQ Queue Depth | `MessageCount` | > 10,000 | Scale workers |
| OpenSearch Cluster | `ClusterStatus.red` | = 1 | PagerDuty |

### Log aggregation

ECS tasks write to CloudWatch Log Groups:

| Log Group | Service |
|-----------|---------|
| `/ecs/estateos-production/api` | Django API |
| `/ecs/estateos-production/worker` | Celery workers |
| `/ecs/estateos-production/beat` | Celery beat |
| `/ecs/estateos-production/nginx` | Nginx reverse proxy |

Query logs with CloudWatch Logs Insights:

```sql
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 50
```

Structured logging fields to include in application logs:

| Field | Description |
|-------|-------------|
| `trace_id` | Request correlation ID |
| `estate_id` | Tenant context |
| `user_id` | Authenticated user |
| `level` | Log level |
| `module` | Source module |

---

## SLIs and SLOs

| SLI | Target SLO | Measurement |
|-----|------------|-------------|
| API availability | 99.9% | `up{job="estateos-backend"}` |
| API latency (p95) | < 500ms | Prometheus histogram |
| WebSocket uptime | 99.5% | Connection success rate |
| Celery task success | 99.5% | `celery_task_failed_total / celery_task_sent_total` |
| Payment processing | 99.99% | Custom business metric |

---

## Alerting

### Prometheus Alertmanager (local)

Add `monitoring/prometheus/alerts.yml` and configure Alertmanager in `prometheus.yml`:

```yaml
rule_files:
  - /etc/prometheus/alerts.yml

alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]
```

### Recommended alert rules

```yaml
groups:
  - name: estateos
    rules:
      - alert: APIDown
        expr: up{job="estateos-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: EstateOS API is down

      - alert: HighAPILatency
        expr: histogram_quantile(0.95, rate(django_http_requests_latency_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: API p95 latency exceeds 1 second

      - alert: CeleryQueueBacklog
        expr: celery_queue_length > 1000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: Celery queue backlog detected
```

---

## Error Tracking (Sentry)

Configure Sentry DSN in environment variables:

```bash
SENTRY_DSN=https://xxx@o123.ingest.sentry.io/456
SENTRY_ENVIRONMENT=production
```

Integrate in Django settings:

```python
import sentry_sdk
sentry_sdk.init(dsn=config("SENTRY_DSN", default=""), environment=config("SENTRY_ENVIRONMENT", default="development"))
```

---

## Health Checks

| Endpoint | Expected | Used By |
|----------|----------|---------|
| `GET /health/` | `{"status": "ok"}` | ALB, Nginx, Docker healthcheck |
| `GET /api/schema/` | OpenAPI schema | Smoke tests |
| RabbitMQ diagnostics | `ping` success | Docker healthcheck |
| Redis `PING` | `PONG` | Docker healthcheck |

---

## Runbook: Common Issues

### High API latency

1. Check Grafana API p95 latency panel
2. Inspect CloudWatch ECS CPU/memory
3. Check RDS `DatabaseConnections` and slow query log
4. Verify Redis cache hit rate

### Celery backlog

1. Check queue depth in Grafana
2. Scale worker ECS service: `aws ecs update-service --desired-count 8`
3. Inspect failed tasks in CloudWatch worker logs
4. Check RabbitMQ memory alarm in management UI

### Search degradation

1. Check OpenSearch cluster health: `GET /_cluster/health`
2. Verify indexing lag in Grafana
3. Review Celery indexing task failures

---

## Related Documentation

- [Deployment Guide](../phase-09/deployment-guide.md)
- [System Architecture](../phase-02/system-architecture.md) — Section 14: Monitoring & Observability
