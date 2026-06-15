# EstateOS — Enterprise Estate Management Platform

Africa's most advanced multi-tenant estate management ecosystem. Production-grade SaaS for residential estates, facility operators, security teams, vendors, and residents.

## Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 5+, DRF, PostgreSQL, Redis, Celery, RabbitMQ, Channels, Elasticsearch |
| Frontend | Next.js 15, React 19, TypeScript, TailwindCSS, ShadCN UI |
| Mobile | React Native (Expo) |
| Infrastructure | Docker, Nginx, Terraform, AWS, GitHub Actions |
| Monitoring | Prometheus, Grafana, Sentry |

## Repository Structure

```
estateos/
├── docs/                 # Phase deliverables (PRD → deployment)
├── backend/              # Django API & WebSocket services
├── frontend/             # Next.js web application
├── mobile/               # Expo React Native app
├── infrastructure/       # Terraform, Docker, Nginx
├── monitoring/             # Prometheus, Grafana configs
└── .github/workflows/    # CI/CD pipelines
```

## Quick Start (Development)

**Requirements:** Python 3.12+, Node 20+, Docker

```bash
# 1. Clone and configure
cp .env.example .env

# 2. Start infrastructure (PostgreSQL, Redis, RabbitMQ, Elasticsearch)
docker compose up -d postgres redis rabbitmq elasticsearch

# 3. Backend (use Python 3.12+)
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python manage.py migrate
python manage.py runserver

# 4. Frontend
cd frontend && npm install && npm run dev

# 5. Mobile
cd mobile && npm install && npx expo start

# Full stack via Docker
docker compose up -d
curl http://localhost/health/
```

## Verification (Latest)

| Check | Result |
|-------|--------|
| Backend tests | **129 passed** |
| Backend coverage | **90%** |
| Frontend build | **24 routes** — production build OK |
| Mobile typecheck | **Pass** |

## Documentation Index

| Phase | Deliverables |
|-------|--------------|
| [Phase 1](docs/phase-01/README.md) | PRD, Functional Spec, User Stories, Acceptance Criteria |
| [Phase 2](docs/phase-02/README.md) | Architecture, ERD, Database Design, API Spec |
| [Phase 3](docs/phase-03/README.md) | Design System, Wireframes, Screens |
| [Phase 4](docs/phase-04/README.md) | Backend Implementation |
| [Phase 5](docs/phase-05/README.md) | Frontend Implementation |
| [Phase 6](docs/phase-06/README.md) | Mobile Implementation |
| [Phase 7](docs/phase-07/README.md) | Testing Strategy & Coverage |
| [Phase 8](docs/phase-08/README.md) | CI/CD Pipelines |
| [Phase 9](docs/phase-09/README.md) | Deployment Guide |
| [Phase 10](docs/phase-10/README.md) | Production Monitoring |

## License

Proprietary — All rights reserved.
