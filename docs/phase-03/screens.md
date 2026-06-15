# EstateOS Screen Specifications

**Phase 3 — High-Fidelity Screen Specs**

Detailed specifications for all major modules. Each screen maps to an implementation path in `frontend/src/app/` (web) or `mobile/app/` (mobile). Design tokens reference `docs/phase-03/tokens.css`.

---

## Global Layout Shell

### Web App Shell

| Region | Component | Spec |
|--------|-----------|------|
| Sidebar | `Sidebar.tsx` | 256px fixed width; collapses to sheet < `lg`; role-filtered items from `navigation.ts` |
| Header | `Header.tsx` | 64px height; estate switcher, search, notifications bell, theme toggle, avatar menu |
| Content | `AppShell.tsx` | Max-width 1400px, padding `px-4 sm:px-6 lg:px-8` |
| Mobile nav | `MobileNav.tsx` | Bottom sheet navigation when sidebar hidden |

### Mobile Tab Shell

| Tab | Route | Icon |
|-----|-------|------|
| Home | `(tabs)/index` | Home |
| Visitors | `(tabs)/visitors` | People |
| Community | `(tabs)/community` | Sparkles |
| Marketplace | `(tabs)/marketplace` | Cart |
| Profile | `(tabs)/profile` | User |

Tab bar: 64px height, active tab `--primary` color, inactive `--muted-foreground`.

---

## Authentication Module

### Login — Web

**Path:** `frontend/src/app/(auth)/login/page.tsx`

| Element | Specification |
|---------|---------------|
| Layout | Centered card (max 420px) on gradient-brand left panel (desktop) |
| Estate selector | Required dropdown; populated from user's memberships |
| Email field | Type email, autocomplete, Zod validation |
| Password field | Toggle visibility icon, min 8 chars |
| Submit | Primary button full-width, loading spinner on submit |
| Biometric | N/A on web |
| Error states | Inline field errors + toast for auth failure |
| Success | Redirect to `/dashboard` or `?redirect=` param |

### Login — Mobile

**Path:** `mobile/app/(auth)/login.tsx`

| Element | Specification |
|---------|---------------|
| Biometric | Face ID / fingerprint button after first successful login |
| Secure storage | Tokens in `expo-secure-store` via `auth.ts` store |
| Keyboard | `KeyboardAvoidingView` with safe area insets |

### Register

**Paths:** `frontend/.../register/page.tsx` · `mobile/app/(auth)/register.tsx`

Multi-step: Account details → Estate/unit selection → Verification pending state.

---

## Dashboard

**Paths:** `frontend/src/app/(dashboard)/dashboard/page.tsx` · `mobile/app/(tabs)/index.tsx`

### Components

| Component | File | Spec |
|-----------|------|------|
| Stat cards | `StatCard.tsx` | 4-up grid; icon badge, value, label, trend arrow |
| Quick actions | `QuickActions.tsx` | Horizontal scroll on mobile; Visitor Pass, Pay Bill, Book Facility, SOS |
| Activity feed | Inline list | Avatar, action text, relative timestamp |
| Notifications | `NotificationPanel.tsx` | Sheet from header bell; mark read, deep links |

### Role Variants

| Role | Visible widgets |
|------|-----------------|
| Resident | Balance, visitors, packages, quick actions |
| Estate Admin | Occupancy rate, revenue, open tickets, security alerts |
| Security | Active passes, gate logs, SOS feed, patrol schedule |
| Finance Admin | Collections, overdue invoices, payment trends |

### Data Sources

- `GET /api/v1/analytics/dashboard/` — aggregated metrics
- `GET /api/v1/notifications/` — unread count
- `GET /api/v1/billing/invoices/?status=unpaid&limit=1` — outstanding balance

---

## Residents

**Path:** `frontend/src/app/(dashboard)/residents/page.tsx`

| Section | Spec |
|---------|------|
| Header | Title + "Add Resident" button (admin only) |
| Filters | Search, unit, status (active/pending/moved-out), resident type |
| Table | Name, unit, type, phone, status badge, actions menu |
| Detail drawer | Profile, family members, vehicles, documents |
| Empty state | Illustration + "No residents match your filters" |

**API:** `GET/POST /api/v1/residents/profiles/`

---

## Visitors

**Paths:** `frontend/.../visitors/page.tsx` · `mobile/app/(tabs)/visitors.tsx` · `mobile/app/visitors/create.tsx` · `mobile/app/visitors/scan.tsx`

### Resident — Pass List

| Element | Spec |
|---------|------|
| Tabs | Active / Expired / Revoked |
| Pass card | Visitor name, valid window, QR thumbnail, share button |
| FAB (mobile) | "+ Create Pass" → `visitors/create` |

### Create Pass Form

| Field | Validation | Required |
|-------|------------|----------|
| Visitor name | 2–100 chars | Yes |
| Phone | E.164 format | Yes |
| Pass type | Single / Multi-day / Permanent | Yes |
| Valid until | Future datetime | Yes |
| Purpose | Max 500 chars | No |
| Vehicle plate | Alphanumeric | No |

**Post-submit:** QR display with share (WhatsApp, SMS, copy link). QR encodes `qr_code` from API.

### Gate Scan (Security)

| State | UI |
|-------|-----|
| Scanning | Full-width camera viewfinder (`expo-camera`) |
| Approved | Green check, visitor details, "Log Entry" CTA |
| Denied | Red X, reason, "Alert Security Lead" |
| Blacklist hit | Destructive banner, auto-notify security |

**API:** `POST /api/v1/visitors/passes/` · `POST /api/v1/visitors/scan/`

---

## Security

**Path:** `frontend/src/app/(dashboard)/security/page.tsx`

| Tab | Content |
|-----|---------|
| Incidents | Table with severity badges, assignee, status workflow |
| SOS Alerts | Real-time feed (WebSocket), map pin, response timer |
| Patrols | Schedule grid, check-in logs |
| Blacklist | Searchable list, add entry form |
| Gate Logs | Filterable entry/exit log with pass reference |

**Roles:** `security_admin`, `security_personnel`, `estate_admin`

**API:** `GET/POST /api/v1/security/incidents/` · `GET /api/v1/security/sos/`

---

## Billing

**Paths:** `frontend/.../billing/page.tsx` · `mobile/app/billing/index.tsx`

| Section | Spec |
|---------|------|
| Balance hero | Large amount typography, due date, "Pay Now" primary CTA |
| Invoice table | Sortable: number, date, amount, status, actions |
| Payment history | Timeline with provider icon (Stripe/Paystack/Flutterwave) |
| Payment methods | Card list, default badge, add/remove |
| Statements | PDF download, date range filter |

### Payment Flow

1. Select invoice → review amount
2. Choose method → provider redirect or inline card form
3. Webhook confirmation → success toast + receipt email
4. Invoice status updates to `paid`

**API:** `GET /api/v1/billing/invoices/` · `POST /api/v1/payments/checkout/`

---

## Utilities

**Path:** `frontend/src/app/(dashboard)/utilities/page.tsx`

| Feature | Spec |
|---------|------|
| Account cards | Per utility type (electricity, water, gas) with meter reading |
| Consumption chart | Monthly bar chart (Recharts), last 12 months |
| Token purchase | Prepaid meter token form, instant delivery |
| Bill history | Linked to billing module invoices |

---

## Marketplace

**Paths:** `frontend/.../marketplace/page.tsx` · `mobile/app/(tabs)/marketplace.tsx`

| Screen | Spec |
|--------|------|
| Browse | Category chips, search, product grid (2-col mobile, 4-col desktop) |
| Product detail | Image carousel, vendor info, reviews, quantity stepper, add to cart |
| Cart | Line items, delivery slot, subtotal, checkout CTA |
| Orders | Status tracker: placed → confirmed → delivered |
| Vendor admin | Product CRUD, order management (vendor role) |

**API:** `GET /api/v1/marketplace/products/` · `POST /api/v1/marketplace/orders/`

---

## Pharmacy

**Path:** `frontend/src/app/(dashboard)/pharmacy/page.tsx`

| Feature | Spec |
|---------|------|
| Prescriptions | Upload photo, OCR assist, refill reminders |
| Orders | Medication list, dosage, delivery/pickup toggle |
| Reminders | Push notification schedule for medication times |

---

## Healthcare

**Path:** `frontend/src/app/(dashboard)/healthcare/page.tsx`

| Feature | Spec |
|---------|------|
| Appointments | Calendar view, hospital/clinic selector, booking form |
| Ambulance | Emergency request with location share |
| Records | Document vault with access controls |

---

## Facilities

**Paths:** `frontend/.../facilities/page.tsx` · `mobile/app/facilities/book.tsx`

| Element | Spec |
|---------|------|
| Facility cards | Image, name, capacity, hourly rate, availability indicator |
| Booking calendar | Week view, slot selection, conflict detection |
| My bookings | Upcoming/past tabs, cancel with policy notice |

**API:** `GET /api/v1/facilities/` · `POST /api/v1/facilities/bookings/`

---

## Maintenance

**Paths:** `frontend/.../maintenance/page.tsx` · `mobile/app/maintenance/create.tsx`

| Element | Spec |
|---------|------|
| Ticket list | Priority badge, category icon, status pipeline |
| Create form | Category, description, photo upload, preferred time |
| Detail view | Timeline of status changes, assignee chat thread |
| Admin view | Kanban board by status column |

**API:** `POST /api/v1/maintenance/tickets/`

---

## Packages

**Path:** `frontend/src/app/(dashboard)/packages/page.tsx`

| Feature | Spec |
|---------|------|
| Incoming | Carrier, tracking number, expected delivery, pickup code |
| Outgoing | Recipient, dispatch status |
| Notifications | Push on arrival at gate/reception |

---

## Parking

**Path:** `frontend/src/app/(dashboard)/parking/page.tsx`

| Feature | Spec |
|---------|------|
| Slot map | Visual grid of assigned/available/EV slots |
| Permits | Vehicle registration, permit expiry |
| EV charging | Session start/stop, kWh consumed, cost |

---

## Community

**Path:** `frontend/src/app/(dashboard)/community/page.tsx` · `mobile/app/(tabs)/community.tsx`

| Tab | Spec |
|-----|------|
| Announcements | Pinned posts, admin badge, rich text |
| Polls | Vote buttons, live results bar chart |
| Groups | Join/leave, member count, group feed |

---

## Transportation

**Path:** `frontend/src/app/(dashboard)/transportation/page.tsx`

| Feature | Spec |
|---------|------|
| Ride request | Pickup/dropoff, vehicle type, fare estimate |
| Shuttle schedule | Route map, next departure countdown |
| Trip history | Past rides with receipt |

---

## Analytics

**Path:** `frontend/src/app/(dashboard)/analytics/page.tsx`

**Roles:** `super_admin`, `estate_admin`, `finance_admin`

| Panel | Visualization |
|-------|---------------|
| Occupancy | Donut chart |
| Revenue | Line chart, monthly trend |
| Visitor traffic | Bar chart by gate |
| Maintenance SLA | Gauge, % resolved within SLA |
| Export | CSV/PDF download buttons |

**API:** `GET /api/v1/analytics/reports/`

---

## AI Concierge

**Paths:** `frontend/.../ai-concierge/page.tsx` · `mobile/app/ai/chat.tsx`

| Element | Spec |
|---------|------|
| Chat window | Scrollable message list, auto-scroll on new message |
| Suggested prompts | Chip row: Book gym, Pay bill, Visitor pass, Report issue |
| AI messages | Markdown rendering, action buttons for confirmed intents |
| User messages | Right-aligned bubble, `--primary` background |
| Input | Text field + send; disabled while streaming |
| Context | Estate ID, user role, recent activity injected server-side |

**API:** `POST /api/v1/ai/chat/` · WebSocket for streaming (future)

---

## Settings

**Path:** `frontend/src/app/(dashboard)/settings/page.tsx`

| Section | Spec |
|---------|------|
| Profile | Name, email, phone, avatar upload |
| Security | Change password, 2FA toggle, active sessions |
| Notifications | Per-channel preferences (email, push, SMS) |
| Appearance | Theme: System / Light / Dark |
| Estate config | Admin only: branding, modules enabled, fee schedules |

---

## SOS (Mobile-First)

**Path:** `mobile/app/sos/index.tsx`

| State | Behavior |
|-------|----------|
| Idle | Pulsing red button, hold 3 seconds to trigger |
| Confirming | Progress ring during hold |
| Active | Full-screen red header, countdown, location shared |
| Resolved | Confirmation + optional incident report |

Long-press prevents accidental activation. Haptic feedback on trigger.

---

## Responsive Behavior Matrix

| Module | Mobile | Tablet | Desktop |
|--------|--------|--------|---------|
| Dashboard | Single column stats | 2-col stats | 4-col stats + sidebar widgets |
| Tables | Card list view | Horizontal scroll table | Full data table |
| Forms | Full-screen steps | Centered card | Side-by-side preview |
| AI Chat | Full screen | Split with suggestions | Fixed width panel (480px) |
| Analytics | Key metrics only | 2×2 grid | Full dashboard |

---

## Interaction States (All Modules)

Every interactive element supports:

| State | Visual |
|-------|--------|
| Default | Token colors as defined |
| Hover | `--accent` background (web) |
| Focus | `ring-2 ring-ring ring-offset-2` |
| Active/Pressed | Scale 0.98, 100ms |
| Disabled | 50% opacity, no pointer events |
| Loading | Spinner in button, skeleton placeholders |
| Empty | Illustration + primary CTA + helper text |
| Error | `--destructive` border/text + retry action |

---

## Related Documentation

- [Design System](./design-system.md)
- [Wireframes](./wireframes.md)
- [Functional Specification](../phase-01/functional-specification.md)
- [Frontend Implementation](../phase-05/README.md)
- [Mobile Implementation](../phase-06/README.md)
