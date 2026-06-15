# Phase 5 — Frontend Implementation

**EstateOS Web Application**

Modern estate management dashboard built with Next.js 15, React 19, Tailwind CSS v4, and ShadCN UI. Serves residents, estate administrators, security personnel, and finance teams.

---

## Overview

| Attribute | Value |
|-----------|-------|
| Framework | Next.js 15 (App Router, Turbopack dev) |
| UI Library | React 19 |
| Styling | Tailwind CSS v4 + CSS custom properties |
| Components | ShadCN UI (Radix primitives) |
| State | Zustand (auth, estate context) |
| Data Fetching | TanStack React Query v5 |
| Forms | React Hook Form + Zod |
| Charts | Recharts |
| Animation | Framer Motion |
| Icons | Lucide React |
| Themes | next-themes (dark/light/system) |

---

## Folder Structure

```
frontend/
├── src/
│   ├── app/                        # Next.js App Router
│   │   ├── layout.tsx              # Root layout (fonts, providers)
│   │   ├── page.tsx                # Landing / redirect
│   │   ├── globals.css             # Tailwind + token imports
│   │   ├── (auth)/                 # Unauthenticated routes
│   │   │   ├── login/
│   │   │   └── register/
│   │   └── (dashboard)/            # Authenticated app shell
│   │       ├── layout.tsx          # Sidebar + header wrapper
│   │       ├── dashboard/
│   │       ├── residents/
│   │       ├── visitors/
│   │       ├── security/
│   │       ├── billing/
│   │       ├── utilities/
│   │       ├── marketplace/
│   │       ├── pharmacy/
│   │       ├── healthcare/
│   │       ├── facilities/
│   │       ├── maintenance/
│   │       ├── packages/
│   │       ├── parking/
│   │       ├── community/
│   │       ├── transportation/
│   │       ├── analytics/
│   │       ├── ai-concierge/
│   │       └── settings/
│   ├── components/
│   │   ├── ui/                     # ShadCN primitives (Button, Card, Dialog…)
│   │   ├── layout/                 # AppShell, Sidebar, Header, MobileNav
│   │   ├── dashboard/              # StatCard, QuickActions, WidgetGrid
│   │   ├── shared/                 # ModulePage scaffold
│   │   └── providers/              # Theme, React Query providers
│   ├── hooks/                      # useAuth, useEstate, useTheme
│   ├── stores/                     # auth-store.ts, estate-store.ts
│   ├── lib/                        # api.ts, auth.ts, navigation.ts, utils.ts
│   ├── styles/
│   │   └── tokens.css              # Design tokens (sync with docs/phase-03/)
│   ├── types/                      # Shared TypeScript types
│   └── middleware.ts               # Auth route protection
├── public/                         # Static assets
├── Dockerfile                      # Multi-stage production build
├── next.config.ts                  # Next.js configuration
├── tailwind.config.ts              # Tailwind v4 config
├── tsconfig.json
└── package.json
```

---

## Architecture Rationale

### App Router with Route Groups

`(auth)` and `(dashboard)` route groups share layouts without affecting URL paths. The dashboard layout wraps all module pages with the persistent sidebar and header, avoiding prop-drilling shell state.

### Module Page Scaffold

Every dashboard module uses `ModulePage.tsx` for consistent page headers, descriptions, and action slots. Module metadata (icons, descriptions) lives in `lib/navigation.ts` — single source of truth for sidebar and page titles.

### Client-Side State vs Server State

| Concern | Tool | Rationale |
|---------|------|-----------|
| Auth tokens, user profile | Zustand (`auth-store`) | Persisted, synchronous access for API client |
| Active estate context | Zustand (`estate-store`) | Drives `X-Estate-Id` header on all requests |
| Server data (lists, details) | React Query | Caching, background refetch, optimistic updates |
| Theme preference | next-themes | System-aware with localStorage persistence |

### API Client

`lib/api.ts` provides a typed fetch wrapper:

- Base URL from `NEXT_PUBLIC_API_URL`
- Auto-attaches `Authorization: Bearer` and `X-Estate-Id` headers
- Handles 401 → token refresh → retry
- Normalizes error responses for toast display

### Role-Based Navigation

`navigation.ts` defines `NAV_ITEMS` with optional `roles` arrays. `getNavItemsForRoles()` filters the sidebar based on the authenticated user's role codes. Admins see all modules; residents see a subset.

### Design Token Integration

Tokens in `src/styles/tokens.css` are imported by `globals.css` and mapped to Tailwind via `@theme inline`. This enables utility classes like `bg-primary`, `text-muted-foreground`, and `rounded-lg` that automatically respect dark mode.

---

## Key Modules

| Route | Page | Primary Roles |
|-------|------|---------------|
| `/dashboard` | Overview widgets, quick actions | All |
| `/residents` | Resident directory | Admin |
| `/visitors` | Pass management | Resident, Security |
| `/security` | Incidents, SOS, patrols | Security, Admin |
| `/billing` | Invoices, payments | Resident, Finance |
| `/marketplace` | Product catalog, orders | Resident |
| `/ai-concierge` | AI chat assistant | All |
| `/analytics` | Reports and charts | Admin, Finance |
| `/settings` | Profile, preferences | All |

Full screen specs: [`docs/phase-03/screens.md`](../phase-03/screens.md)

---

## Local Development

### Prerequisites

- Node.js 20+
- Backend running on port 8000 (Docker Compose or local)

### Setup

```bash
cd frontend
npm install

cp .env.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Run

```bash
npm run dev        # http://localhost:3000 (Turbopack)
npm run build      # Production build
npm run start      # Serve production build
npm run lint       # ESLint
npm run typecheck  # TypeScript check
```

### With Docker Compose

Frontend starts automatically on port 3000 when running `docker compose up -d` from the repository root.

---

## Production Build

### Docker Multi-Stage

The `frontend/Dockerfile` uses a multi-stage build:

1. **deps** — Install node_modules
2. **builder** — `next build` with standalone output
3. **production** — Minimal Node.js image serving standalone server

```bash
docker build -t estateos/frontend:latest --target production ./frontend
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL |
| `NEXT_PUBLIC_APP_URL` | Frontend canonical URL (OAuth redirects) |

### Deployment

Production frontend deploys as:

- **ECS Fargate** service behind CloudFront CDN (via `infrastructure/terraform/modules/cloudfront/`)
- Static assets cached at edge; API calls proxied to ALB

CI builds and pushes to ECR on merge to `main` (`.github/workflows/deploy.yml`).

---

## Authentication Flow

1. User submits login form → `POST /api/v1/accounts/auth/token/`
2. Access + refresh tokens stored in `auth-store`
3. `middleware.ts` redirects unauthenticated users from `(dashboard)` routes to `/login`
4. Estate selector populates from user's memberships
5. Selected estate ID persisted in `estate-store` → sent as `X-Estate-Id`

---

## Theming

Theme provider wraps the app in `layout.tsx`. Users toggle via header control. CSS class `.dark` on `<html>` swaps token values defined in `tokens.css`.

Custom utilities in `globals.css`:

- `.gradient-brand` — Primary gradient background
- `.glass` — Frosted glass effect for overlays
- `.container-app` — Max-width content wrapper

Design system reference: [`docs/phase-03/design-system.md`](../phase-03/design-system.md)

---

## Related Documentation

- [Design System](../phase-03/design-system.md)
- [Screen Specifications](../phase-03/screens.md)
- [Backend Implementation](../phase-04/README.md)
- [Deployment Guide](../phase-09/deployment-guide.md)
- [CI/CD Pipeline](../phase-08/README.md)
