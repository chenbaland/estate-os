# Phase 10 — Production Monitoring

**EstateOS Observability Overview**

Production monitoring strategy for the EstateOS platform — metrics, logs, dashboards, alerting, and on-call runbooks. For detailed configuration and procedures, see the comprehensive [**Monitoring Guide**](./monitoring-guide.md).

---

## Overview

EstateOS observability spans three environments:

| Environment | Stack | Purpose |
|-------------|-------|---------|
| Local (compose prod) | Prometheus + Grafana | Development debugging, dashboard prototyping |
| AWS Production | CloudWatch + Container Insights | Infrastructure and application metrics |
| All environments | Sentry | Error tracking and release health |

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Application │───▶│  Prometheus  │───▶│   Grafana    │
│  /metrics    │    │  (local)     │    │  Dashboards  │
└──────────────┘    └──────────────┘    └──────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  ECS Tasks   │───▶│  CloudWatch  │───▶│   Alarms     │
│  Logs/Metrics│    │  Logs/Metrics│    │  PagerDuty   │
└──────────────┘    └──────────────┘    └──────────────┘

┌──────────────┐    ┌──────────────┐
│  Django/Next │───▶│   Sentry     │
│  Exceptions  │    │   Issues     │
└──────────────┘    └──────────────┘
```

---

## Monitoring Stack Locations

| Component | Path |
|-----------|------|
| Prometheus config | `monitoring/prometheus/prometheus.yml` |
| Grafana dashboards | `monitoring/grafana/dashboards/` |
| Grafana provisioning | `monitoring/grafana/provisioning/` |
| Docker compose overlay | `docker-compose.prod.yml` (Prometheus + Grafana services) |
| Nginx stub status | `infrastructure/nginx/nginx.conf` |

---

## Key Metrics

### Application (SLIs)

| SLI | Target SLO | Measurement |
|-----|------------|-------------|
| API availability | 99.9% | `up{job="estateos-backend"}` |
| API latency (p95) | < 500ms | Prometheus histogram |
| WebSocket uptime | 99.5% | Connection success rate |
| Celery task success | 99.5% | Failed / sent ratio |
| Payment processing | 99.99% | Custom business metric |

See [SLIs and SLOs](./monitoring-guide.md#slis-and-slos) in the monitoring guide.

### Infrastructure

| Service | Key Metrics |
|---------|-------------|
| ECS (API) | CPU, memory, running task count |
| RDS PostgreSQL | Connections, storage, read/write latency |
| ElastiCache Redis | Memory usage, hit rate, connections |
| Amazon MQ | Queue depth, message rates |
| OpenSearch | Cluster health, indexing lag |
| ALB | Request count, unhealthy hosts, latency |

---

## Dashboards

### EstateOS Overview (Grafana)

Pre-provisioned dashboard: `monitoring/grafana/dashboards/estateos-overview.json`

Panels include:

- API request rate and p95 latency
- Celery queue depth
- Redis connections and memory
- PostgreSQL active connections
- Service health indicators (API, Redis, RabbitMQ, Elasticsearch)

**Local access:**

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d prometheus grafana
# Grafana: http://localhost:3001
```

### CloudWatch (Production)

ECS Container Insights provides automatic dashboards for:

- CPU and memory utilization per service
- Running task count
- Network I/O

RDS, ElastiCache, Amazon MQ, and OpenSearch emit metrics automatically.

---

## Alerting

### Production Alarms (CloudWatch)

| Alarm | Threshold | Action |
|-------|-----------|--------|
| API High CPU | > 80% for 5 min | Scale out ECS |
| API Unhealthy | ALB unhealthy > 0 for 2 min | PagerDuty |
| RDS Storage | < 10 GB free | Email alert |
| Redis Memory | > 80% usage | Scale up |
| MQ Queue Depth | > 10,000 messages | Scale workers |
| OpenSearch Cluster | Status red | PagerDuty |

### Prometheus Alertmanager (Local)

Recommended rules documented in [monitoring-guide.md](./monitoring-guide.md#alerting):

- `APIDown` — backend scrape target unreachable
- `HighAPILatency` — p95 > 1 second for 5 minutes
- `CeleryQueueBacklog` — queue length > 1000 for 10 minutes

---

## Logging

### Structured Log Fields

| Field | Description |
|-------|-------------|
| `trace_id` | Request correlation ID |
| `estate_id` | Tenant context |
| `user_id` | Authenticated user |
| `level` | Log level |
| `module` | Source module |

### CloudWatch Log Groups (Production)

| Log Group | Service |
|-----------|---------|
| `/ecs/estateos-production/api` | Django API |
| `/ecs/estateos-production/worker` | Celery workers |
| `/ecs/estateos-production/beat` | Celery beat |
| `/ecs/estateos-production/nginx` | Nginx reverse proxy |

Query errors with CloudWatch Logs Insights:

```sql
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 50
```

---

## Error Tracking (Sentry)

Configure via environment variables:

```bash
SENTRY_DSN=https://xxx@o123.ingest.sentry.io/456
SENTRY_ENVIRONMENT=production
```

Integrated in Django settings for backend exceptions. Frontend and mobile Sentry SDK integration recommended for production releases.

---

## Health Checks

| Endpoint | Expected | Used By |
|----------|----------|---------|
| `GET /health/` | `{"status": "ok"}` | ALB, Nginx, Docker, ECS |
| `GET /api/schema/` | OpenAPI schema | Smoke tests, deploy validation |
| RabbitMQ diagnostics | `ping` success | Docker healthcheck |
| Redis `PING` | `PONG` | Docker healthcheck |

Post-deploy verification:

```bash
curl -f https://api.estateos.app/health/
```

---

## Runbooks

Quick reference for common incidents. Full procedures in [monitoring-guide.md](./monitoring-guide.md#runbook-common-issues).

### High API Latency

1. Check Grafana API p95 latency panel
2. Inspect CloudWatch ECS CPU/memory
3. Check RDS connections and slow query log
4. Verify Redis cache hit rate

### Celery Backlog

1. Check queue depth in Grafana
2. Scale worker ECS service
3. Inspect failed tasks in CloudWatch worker logs
4. Check RabbitMQ memory alarm

### Search Degradation

1. Check OpenSearch cluster health
2. Verify indexing lag in Grafana
3. Review Celery indexing task failures

---

## On-Call Escalation

| Severity | Examples | Response Time | Channel |
|----------|----------|---------------|---------|
| P1 — Critical | API down, SOS failures, payment outage | 15 min | PagerDuty |
| P2 — High | Elevated latency, Celery backlog | 1 hour | Slack + email |
| P3 — Medium | Single service degradation | 4 hours | Slack |
| P4 — Low | Non-critical warnings | Next business day | Ticket |

---

## Getting Started

1. **Local monitoring:** Start Prometheus + Grafana via compose prod overlay
2. **Review dashboards:** Open EstateOS Overview in Grafana
3. **Configure Sentry:** Set `SENTRY_DSN` in environment
4. **Production:** Verify CloudWatch alarms are active post-deploy
5. **Read the full guide:** [monitoring-guide.md](./monitoring-guide.md)

---

## Related Documentation

- [**Monitoring Guide (detailed)**](./monitoring-guide.md)
- [Deployment Guide](../phase-09/deployment-guide.md)
- [CI/CD Pipeline](../phase-08/README.md)
- [System Architecture](../phase-02/system-architecture.md) — Section 14: Monitoring & Observability
- [Testing Strategy](../phase-07/README.md)
