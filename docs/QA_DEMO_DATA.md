# EstateOS QA & Demo Data Guide

Use this guide for holistic manual QA across **super admin**, **estate admin**, **specialist admins**, and **resident** dashboards.

## Seed the database

From the backend directory (with migrations applied):

```bash
cd backend
source .venv/bin/activate
python manage.py seed_demo          # idempotent — safe to re-run
python manage.py seed_demo --flush  # wipe demo data first, then re-seed
```

**Default password for all demo accounts:** `DemoPass12345`

---

## Demo estates

| Estate | Slug | City | Purpose |
|--------|------|------|---------|
| Palm Grove Demo Estate | `palm-grove-demo` | Lagos | Primary QA estate — full module coverage |
| Oak Heights Demo Estate | `oak-heights-demo` | Abuja | Secondary tenant — cross-estate isolation tests |

---

## Login credentials

Base URL (local): `http://localhost:3000/login`

### Platform super admin

| Email | Password | Lands on |
|-------|----------|----------|
| `superadmin@demo.estateos` | `DemoPass12345` | `/platform` |

**Platform routes:** `/platform`, `/platform/estates`, `/platform/admins`, `/platform/audit-logs`

### Palm Grove Demo (`palm-grove-demo`)

| Role | Email | Password |
|------|-------|----------|
| Estate admin | `admin@palmgrovedemo.estateos` | `DemoPass12345` |
| Finance admin | `finance@palmgrovedemo.estateos` | `DemoPass12345` |
| Security admin | `security-admin@palmgrovedemo.estateos` | `DemoPass12345` |
| Facility admin | `facility@palmgrovedemo.estateos` | `DemoPass12345` |
| Active resident (owner, A-101) | `resident1@palmgrovedemo.estateos` | `DemoPass12345` |
| Pending resident (A-102) | `resident2@palmgrovedemo.estateos` | `DemoPass12345` |
| Active tenant (A-103) | `tenant@palmgrovedemo.estateos` | `DemoPass12345` |
| Vendor | `vendor@palmgrovedemo.estateos` | `DemoPass12345` |
| Technician | `technician@palmgrovedemo.estateos` | `DemoPass12345` |
| Security personnel | `security-staff@palmgrovedemo.estateos` | `DemoPass12345` |

### Oak Heights Demo (`oak-heights-demo`)

| Role | Email | Password |
|------|-------|----------|
| Estate admin | `admin@oakheightsdemo.estateos` | `DemoPass12345` |
| Active resident (T1-501) | `resident1@oakheightsdemo.estateos` | `DemoPass12345` |

---

## Seeded module data (Palm Grove)

| Module | Sample records | QA focus |
|--------|----------------|----------|
| Residents | Active owner, pending approval, tenant, family member, vehicle | Approval flow, profiles, gate access |
| Visitors | Active pass, entry log, blacklist entry | QR gate flow, deny list |
| Billing | Issued + overdue invoices, partial payment, debt record | Finance admin views, resident billing |
| Payments | Paystack provider config | Checkout configuration |
| Security | Incident, patrol log, SOS alert, emergency broadcast | Security admin dashboard |
| Maintenance | 2 tickets (open + in progress), SLA config | Technician assignment |
| Facilities | Gym + confirmed booking | Resident booking |
| Packages | Package awaiting pickup + log | Gate house workflow |
| Parking | Occupied slot + active permit | Resident parking |
| Utilities | Electricity account + token purchase | Utility top-up |
| Marketplace | Vendor, product, pending order | Vendor + resident commerce |
| Community | Post, comment, poll, announcement, lost & found | Resident engagement |
| Healthcare | Partner clinic + confirmed appointment | Resident health booking |
| Pharmacy | Verified prescription + medication order | Prescription fulfillment |
| Transportation | Ride request | Mobility module |
| Analytics | Metric snapshots + dashboard widget | Analytics pages |
| Notifications | In-app template + delivered notification | Notification panel |
| AI | Conversation, indexed handbook, payment-risk prediction | AI assistant pages |
| Platform audit | Estate created + admin assigned entries | Super admin audit log |

Oak Heights has structure, admin, and one resident only — use it to verify **tenant isolation** (data from Palm Grove must not appear when `X-Estate-Id` is Oak Heights).

---

## Recommended QA scenarios

### 1. Super admin (no approval gate)

1. Log in as `superadmin@demo.estateos`.
2. Confirm redirect to `/platform` (not `/dashboard` or `/pending-approval`).
3. Overview shows ≥2 estates, pending registrations ≥1.
4. Estates list includes both demo estates; create/edit/deactivate works.
5. Audit logs show seeded platform actions.

### 2. Pending resident approval

1. Log in as `admin@palmgrovedemo.estateos`.
2. Open residents module — find **Emeka Nwosu** (pending, unit A-102).
3. Activate resident and assign type — confirm they can log in without `/pending-approval`.

3. Log in as `resident2@palmgrovedemo.estateos` **before** activation — should land on `/pending-approval`.

### 3. Role-based navigation

| User | Should see | Should NOT see |
|------|------------|----------------|
| Estate admin | Full estate modules, analytics | Platform console |
| Finance admin | Billing, invoices, debts | Full security admin tools (unless permitted) |
| Security admin | Visitors, security, patrols | Platform console |
| Resident | Billing (own), community, visitors (own) | Platform, estate admin settings |
| Super admin | Platform console, create estate | Resident-only flows without estate context |

### 4. Cross-tenant isolation

1. Log in as `resident1@palmgrovedemo.estateos` — note invoices, visitors, packages.
2. Log in as `resident1@oakheightsdemo.estateos` — must see **only** Oak Heights data (no Palm Grove invoices/packages).

### 5. Module smoke tests

For each sidebar module under Palm Grove admin/resident roles, confirm list pages return seeded rows (not empty states):

- Visitors → pass `QR-DEMO-PALM-001`
- Billing → `INV-DEMO-2026-0001`, overdue invoice
- Maintenance → `MT-DEMO-0001`
- Packages → `PKG-DEMO-001`
- Marketplace → order `ORD-DEMO-0001`

### 6. Registration (new user)

1. Register a new user selecting **Palm Grove Demo** and unit **A-104** (vacant).
2. Confirm pending state until estate admin activates.

---

## Known frontend note

The main estate **dashboard home** (`/dashboard`) still uses placeholder stat cards. Module **list/detail pages** and the **platform console** use live API data — use those for data-driven QA until dashboard widgets are wired to analytics APIs.

---

## Reset demo data

```bash
python manage.py seed_demo --flush
```

This removes users with `@demo.estateos` emails and estates with slugs `palm-grove-demo` / `oak-heights-demo`, then re-seeds.

---

## Automated test

```bash
cd backend
DJANGO_SETTINGS_MODULE=config.settings.test pytest core/tests/test_seed_demo.py -q
```
