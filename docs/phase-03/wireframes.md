# EstateOS Wireframes

**Phase 3 — ASCII / Text Wireframes**

Low-fidelity wireframes for key user flows across web (`frontend/`) and mobile (`mobile/`). Dimensions assume mobile-first (375×812) unless noted as desktop (1440×900).

Legend: `[ ]` button/input · `( )` radio/checkbox · `│` divider · `▓` primary action · `⚠` destructive/SOS

---

## 1. Login

**Routes:** Web `frontend/src/app/(auth)/login/` · Mobile `mobile/app/(auth)/login.tsx`

### Mobile — Resident Login

```
┌─────────────────────────────────────┐
│                                     │
│         [EstateOS Logo]             │
│                                     │
│    Welcome back                     │
│    Sign in to your estate           │
│                                     │
│  Estate                            │
│  ┌─────────────────────────────┐   │
│  │ Select estate          ▼   │   │
│  └─────────────────────────────┘   │
│                                     │
│  Email                              │
│  ┌─────────────────────────────┐   │
│  │ you@example.com             │   │
│  └─────────────────────────────┘   │
│                                     │
│  Password                           │
│  ┌─────────────────────────────┐   │
│  │ ••••••••              👁   │   │
│  └─────────────────────────────┘   │
│                                     │
│  [ ] Remember me    Forgot password?│
│                                     │
│  ┌─────────────────────────────┐   │
│  │      ▓ Sign In              │   │
│  └─────────────────────────────┘   │
│                                     │
│  ─────────── or ───────────         │
│                                     │
│  [  Continue with Face ID  ]        │
│                                     │
│  Don't have an account? Register    │
│                                     │
└─────────────────────────────────────┘
```

### Desktop — Split Layout

```
┌──────────────────────┬──────────────────────────────────────────┐
│                      │                                          │
│   gradient-brand     │   Welcome back                           │
│                      │                                          │
│   [Illustration]     │   Estate    [ Select estate        ▼ ]   │
│   Smart estate       │   Email     [ ______________________ ]   │
│   management         │   Password  [ ______________________ ]   │
│                      │                                          │
│                      │   [ ] Remember    Forgot password?       │
│                      │   [ ▓ Sign In ]                          │
│                      │   ───── or ─────                         │
│                      │   [ Continue with SSO ]                  │
│                      │   Register →                             │
└──────────────────────┴──────────────────────────────────────────┘
```

---

## 2. Dashboard

**Routes:** Web `frontend/src/app/(dashboard)/dashboard/` · Mobile `mobile/app/(tabs)/index.tsx`

### Desktop — Resident Dashboard

```
┌────────┬────────────────────────────────────────────────────────────┐
│        │  Good morning, Ada  🔔 ⚙ 🌙                               │
│  NAV   ├────────────────────────────────────────────────────────────┤
│        │                                                            │
│ ● Dash │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│   Res  │  │ ₦45,200  │ │ 2 Active │ │ 1 Package│ │ 0 Alerts │      │
│   Vis  │  │ Due Mar15│ │ Visitors │ │ Pending  │ │ Security │      │
│   Bill │  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│   ...  │                                                            │
│        │  Quick Actions                                             │
│        │  [+ Visitor Pass] [Pay Bill] [Book Facility] [SOS ⚠]      │
│        │                                                            │
│        │  Recent Activity                    Upcoming               │
│        │  ┌─────────────────────────┐  ┌─────────────────────┐     │
│        │  │ • Visitor checked in    │  │ Gym — Today 6pm     │     │
│        │  │ • Payment received      │  │ Invoice due Mar 15  │     │
│        │  │ • Maintenance resolved  │  │ Community BBQ Sat   │     │
│        │  └─────────────────────────┘  └─────────────────────┘     │
│        │                                                            │
│        │  Announcements                                             │
│        │  ┌────────────────────────────────────────────────────┐   │
│        │  │ 🏊 Pool maintenance — Mar 12–14                   │   │
│        │  └────────────────────────────────────────────────────┘   │
└────────┴────────────────────────────────────────────────────────────┘
```

### Mobile — Home Tab

```
┌─────────────────────────────────────┐
│  Lagos Heights Estate        🔔     │
│  Unit B-204 · Ada Okonkwo           │
├─────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐            │
│  │ ₦45,200 │ │ 2 Vis   │            │
│  │ Due soon│ │ Active  │            │
│  └─────────┘ └─────────┘            │
│                                     │
│  Quick Actions                      │
│  [Pass] [Pay] [Book] [SOS⚠]         │
│                                     │
│  Recent                             │
│  ┌─────────────────────────────┐   │
│  │ 👤 Chidi arrived — Gate 1   │   │
│  │ 💳 Payment confirmed        │   │
│  └─────────────────────────────┘   │
│                                     │
├─────────────────────────────────────┤
│  🏠    👥    ✨    🛒    👤         │
│ Home  Vis  Comm  Shop  Profile     │
└─────────────────────────────────────┘
```

---

## 3. Visitor Pass Creation

**Routes:** Web `frontend/src/app/(dashboard)/visitors/` · Mobile `mobile/app/visitors/create.tsx`

### Mobile — Create Pass (Step 1: Details)

```
┌─────────────────────────────────────┐
│  ←  Create Visitor Pass             │
├─────────────────────────────────────┤
│                                     │
│  Visitor Name *                     │
│  ┌─────────────────────────────┐   │
│  │ Chidi Okafor                │   │
│  └─────────────────────────────┘   │
│                                     │
│  Phone Number *                     │
│  ┌─────────────────────────────┐   │
│  │ +234 801 234 5678           │   │
│  └─────────────────────────────┘   │
│                                     │
│  Pass Type                          │
│  ( ) Single entry  (●) Multi-day    │
│                                     │
│  Valid Until                        │
│  ┌─────────────────────────────┐   │
│  │ Mar 11, 2026 · 6:00 PM   📅  │   │
│  └─────────────────────────────┘   │
│                                     │
│  Purpose                            │
│  ┌─────────────────────────────┐   │
│  │ Family visit                │   │
│  └─────────────────────────────┘   │
│                                     │
│  [ ] Notify security on arrival     │
│                                     │
│  ┌─────────────────────────────┐   │
│  │      ▓ Generate Pass        │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

### Mobile — Pass Generated (Step 2: QR)

```
┌─────────────────────────────────────┐
│  ←  Visitor Pass                    │
├─────────────────────────────────────┤
│                                     │
│         ┌───────────────┐           │
│         │               │           │
│         │   [QR CODE]   │           │
│         │               │           │
│         └───────────────┘           │
│                                     │
│         Chidi Okafor                  │
│         Valid until 6:00 PM          │
│         Pass #VP-2026-0042           │
│                                     │
│  ┌──────────┐  ┌──────────┐         │
│  │ Share 📤 │  │ Save 📥  │         │
│  └──────────┘  └──────────┘         │
│                                     │
│  ┌─────────────────────────────┐   │
│  │      Revoke Pass            │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

---

## 4. Gate Scan

**Routes:** Mobile `mobile/app/visitors/scan.tsx` · Web Security module

### Mobile — Security Gate Scanner

```
┌─────────────────────────────────────┐
│  ←  Gate Scanner          Gate 1    │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  │     [ CAMERA VIEWFINDER ]   │   │
│  │         Scan QR code        │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  ─── or enter code manually ───     │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ VP-2026-0042                │   │
│  └─────────────────────────────┘   │
│  [ Verify ]                         │
│                                     │
├─────────────────────────────────────┤
│  LAST SCAN                          │
│  ✅ Chidi Okafor — Approved 2:14pm  │
└─────────────────────────────────────┘
```

### Scan Result — Approved

```
┌─────────────────────────────────────┐
│                                     │
│            ✅                        │
│         ACCESS GRANTED              │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  👤 Chidi Okafor            │   │
│  │  Host: Ada Okonkwo · B-204  │   │
│  │  Purpose: Family visit      │   │
│  │  Valid: until 6:00 PM         │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │      ▓ Log Entry            │   │
│  └─────────────────────────────┘   │
│  [ Deny Entry ]                     │
│                                     │
└─────────────────────────────────────┘
```

### Scan Result — Denied (Blacklist)

```
┌─────────────────────────────────────┐
│                                     │
│            ⛔                        │
│         ACCESS DENIED               │
│                                     │
│  Visitor on estate blacklist        │
│  Reason: Previous trespass          │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  ⚠ Alert Security Lead      │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

---

## 5. SOS Emergency

**Routes:** Mobile `mobile/app/sos/index.tsx` · Web Security module alerts

### Mobile — SOS Trigger

```
┌─────────────────────────────────────┐
│  ←  Emergency SOS                   │
├─────────────────────────────────────┤
│                                     │
│         ⚠                           │
│    Hold to send SOS alert           │
│                                     │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  │      [ HOLD 3 SEC ]         │   │
│  │         ⚠ SOS               │   │
│  │      (pulsing ring)         │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  Your location will be shared       │
│  with estate security immediately.  │
│                                     │
│  Emergency type (optional)          │
│  [Medical] [Security] [Fire] [Other]│
│                                     │
│  Emergency contacts                 │
│  📞 Estate Security  +234 800 ...   │
│  📞 Police           112            │
│                                     │
└─────────────────────────────────────┘
```

### SOS Active State

```
┌─────────────────────────────────────┐
│                                     │
│         🔴 SOS ACTIVE               │
│                                     │
│  Alert sent to security at 2:31 PM  │
│  Unit B-204 · Gate area             │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Security en route (~3 min) │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  📞 Call Security           │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Cancel SOS (confirm)       │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

---

## 6. Billing

**Routes:** Web `frontend/src/app/(dashboard)/billing/` · Mobile `mobile/app/billing/index.tsx`

### Desktop — Billing Overview

```
┌────────┬────────────────────────────────────────────────────────────┐
│  NAV   │  Billing                              [ Pay Now ▓ ]          │
│        ├────────────────────────────────────────────────────────────┤
│        │  ┌─────────────────────────────────────────────────────┐ │
│        │  │ Outstanding Balance          ₦45,200.00              │ │
│        │  │ Due: March 15, 2026 · Service charge Q1              │ │
│        │  └─────────────────────────────────────────────────────┘ │
│        │                                                            │
│        │  [ Invoices ] [ Payments ] [ Statements ]                │
│        │  ─────────────────────────────────────────                 │
│        │                                                            │
│        │  Invoice #    Date        Amount      Status    Action     │
│        │  INV-2026-042 Mar 01     ₦45,200     Unpaid    [ Pay ]    │
│        │  INV-2026-031 Feb 01     ₦45,200     Paid      [ View ]   │
│        │  INV-2026-018 Jan 01     ₦45,200     Paid      [ View ]   │
│        │                                                            │
│        │  Payment Methods                                           │
│        │  💳 Visa ···· 4242  [Default]  [+ Add method]              │
│        │                                                            │
└────────┴────────────────────────────────────────────────────────────┘
```

### Mobile — Pay Invoice Flow

```
┌─────────────────────────────────────┐
│  ←  Pay Invoice                     │
├─────────────────────────────────────┤
│                                     │
│  INV-2026-042                       │
│  Service Charge — Q1 2026           │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Total          ₦45,200.00  │   │
│  └─────────────────────────────┘   │
│                                     │
│  Payment Method                     │
│  (●) Card ···· 4242                 │
│  ( ) Paystack                       │
│  ( ) Bank Transfer                  │
│                                     │
│  ┌─────────────────────────────┐   │
│  │      ▓ Pay ₦45,200          │   │
│  └─────────────────────────────┘   │
│                                     │
│  🔒 Secured by Stripe / Paystack    │
│                                     │
└─────────────────────────────────────┘
```

---

## 7. Marketplace

**Routes:** Web `frontend/src/app/(dashboard)/marketplace/` · Mobile `mobile/app/(tabs)/marketplace.tsx`

### Mobile — Marketplace Browse

```
┌─────────────────────────────────────┐
│  Marketplace                  🔍    │
├─────────────────────────────────────┤
│  [All] [Food] [Services] [Retail]   │
│                                     │
│  Featured                           │
│  ┌──────────┐ ┌──────────┐          │
│  │ [img]    │ │ [img]    │          │
│  │ Fresh    │ │ Laundry  │          │
│  │ Baskets  │ │ Express  │          │
│  │ ₦8,500   │ │ ₦2,000   │          │
│  └──────────┘ └──────────┘          │
│                                     │
│  All Products                       │
│  ┌─────────────────────────────┐   │
│  │ [img] Organic Veg Box       │   │
│  │ Green Farms · ₦8,500  [+]   │   │
│  ├─────────────────────────────┤   │
│  │ [img] Home Cleaning (2hr)   │   │
│  │ CleanPro · ₦12,000    [+]   │   │
│  ├─────────────────────────────┤   │
│  │ [img] Generator Service     │   │
│  │ PowerFix · ₦25,000    [+]   │   │
│  └─────────────────────────────┘   │
│                                     │
├─────────────────────────────────────┤
│  🏠    👥    ✨    🛒    👤         │
└─────────────────────────────────────┘
```

### Product Detail + Cart

```
┌─────────────────────────────────────┐
│  ←  Organic Veg Box                 │
├─────────────────────────────────────┤
│  ┌─────────────────────────────┐   │
│  │        [ Product Image ]    │   │
│  └─────────────────────────────┘   │
│                                     │
│  Green Farms                        │
│  ★ 4.8 (124 reviews)                │
│                                     │
│  ₦8,500                             │
│  Weekly delivery of seasonal        │
│  vegetables from local farms.       │
│                                     │
│  Quantity  [ − ]  1  [ + ]          │
│                                     │
│  Delivery: Tomorrow by 10 AM        │
│                                     │
│  ┌─────────────────────────────┐   │
│  │   ▓ Add to Cart — ₦8,500    │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

---

## 8. AI Concierge

**Routes:** Web `frontend/src/app/(dashboard)/ai-concierge/` · Mobile `mobile/app/ai/chat.tsx`

### Desktop — Chat Interface

```
┌────────┬────────────────────────────────────────────────────────────┐
│  NAV   │  AI Concierge                          [ New chat ]         │
│        ├────────────────────────────────────────────────────────────┤
│        │  Suggested prompts:                                        │
│        │  [Book gym] [Pay bill] [Visitor pass] [Report issue]       │
│        │                                                            │
│        │  ┌────────────────────────────────────────────────────┐   │
│        │  │ 🤖 Hi Ada! I'm your estate assistant. How can I     │   │
│        │  │    help you today?                                   │   │
│        │  └────────────────────────────────────────────────────┘   │
│        │                                                            │
│        │  ┌────────────────────────────────────────────────────┐   │
│        │  │ 👤 Book the tennis court for Saturday at 4pm       │   │
│        │  └────────────────────────────────────────────────────┘   │
│        │                                                            │
│        │  ┌────────────────────────────────────────────────────┐   │
│        │  │ 🤖 Tennis court is available Sat 4–5 PM.           │   │
│        │  │    [ Confirm Booking ]  [ See alternatives ]       │   │
│        │  └────────────────────────────────────────────────────┘   │
│        │                                                            │
│        │  ┌──────────────────────────────────────────┐  [ Send ▓]│
│        │  │ Ask anything about your estate...         │           │
│        │  └──────────────────────────────────────────┘           │
└────────┴────────────────────────────────────────────────────────────┘
```

### Mobile — AI Chat

```
┌─────────────────────────────────────┐
│  ←  AI Concierge                    │
├─────────────────────────────────────┤
│  [Book gym] [Pay bill] [Visitor]    │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 🤖 How can I help?          │   │
│  └─────────────────────────────┘   │
│                                     │
│       ┌─────────────────────────┐ │
│       │ 👤 When is my bill due? │ │
│       └─────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 🤖 Your Q1 service charge │   │
│  │ of ₦45,200 is due Mar 15. │   │
│  │ [ Pay Now ]               │   │
│  └─────────────────────────────┘   │
│                                     │
├─────────────────────────────────────┤
│  [ Ask anything...          ] [▓]  │
└─────────────────────────────────────┘
```

---

## Flow Summary

| Flow | Primary Actor | Entry Point | Key API |
|------|---------------|-------------|---------|
| Login | All users | `/login` | `POST /api/v1/accounts/auth/token/` |
| Dashboard | Resident, Admin | `/dashboard` | Multiple module endpoints |
| Visitor Pass | Resident | `/visitors/create` | `POST /api/v1/visitors/passes/` |
| Gate Scan | Security | `/visitors/scan` | `POST /api/v1/visitors/scan/` |
| SOS | Resident | `/sos` | `POST /api/v1/security/sos/` |
| Billing | Resident | `/billing` | `GET /api/v1/billing/invoices/` |
| Marketplace | Resident | `/marketplace` | `GET /api/v1/marketplace/products/` |
| AI Concierge | Resident | `/ai-concierge` | `POST /api/v1/ai/chat/` |

---

## Related Documentation

- [Design System](./design-system.md)
- [Screen Specifications](./screens.md)
- [API Specification](../phase-02/api-specification.md)
