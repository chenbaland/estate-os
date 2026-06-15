# EstateOS — Acceptance Criteria

Criteria use **Given / When / Then** format. All criteria must pass for module sign-off.

---

## Module 1: Authentication & Authorization

### AC-AUTH-001: Email Login
- **Given** a registered user with verified email
- **When** they submit valid email and password to `POST /api/v1/auth/login/`
- **Then** receive JWT access (15 min) and refresh (7 days) tokens
- **And** response includes user profile and accessible estates
- **And** failed attempts are logged; account locks after 5 failures in 15 min

### AC-AUTH-002: Phone OTP Login
- **Given** a user with verified phone number
- **When** they request OTP via `POST /api/v1/auth/otp/request/`
- **Then** OTP is sent via SMS within 30 seconds
- **And** OTP expires after 10 minutes
- **When** valid OTP submitted within 3 attempts
- **Then** JWT tokens issued

### AC-AUTH-003: OAuth Login (Google/Apple)
- **Given** valid OAuth credentials configured
- **When** user completes OAuth flow
- **Then** account created or linked if email matches
- **And** JWT tokens issued
- **And** OAuth tokens not stored in plaintext

### AC-AUTH-004: MFA
- **Given** MFA enabled on account
- **When** user logs in with valid credentials
- **Then** MFA challenge required before tokens issued
- **When** valid TOTP submitted
- **Then** tokens issued and session recorded
- **And** 10 backup codes generated on setup; each usable once

### AC-AUTH-005: RBAC
- **Given** user assigned `security_admin` role in Estate A
- **When** accessing Estate B resources
- **Then** receive 403 Forbidden
- **When** accessing permitted resource in Estate A
- **Then** receive 200 OK

### AC-AUTH-006: Session Management
- **Given** user with 3 active sessions
- **When** revoking session ID via API
- **Then** that session's refresh token invalidated
- **And** other sessions remain active

### AC-AUTH-007: Rate Limiting
- **Given** auth endpoints
- **When** > 20 requests/min from single IP
- **Then** receive 429 Too Many Requests

---

## Module 2: Resident Management

### AC-RES-001: Onboarding
- **Given** estate admin sends invite to email
- **When** resident completes registration and admin allocates unit
- **Then** resident status becomes ACTIVE
- **And** resident appears in estate directory
- **And** audit log records allocation

### AC-RES-002: Family Members
- **Given** primary resident with 2 family member slots (estate policy)
- **When** adding 3rd family member
- **Then** receive validation error
- **When** adding within limit
- **Then** family member linked with configured access level

### AC-RES-003: Vehicles
- **Given** resident registers vehicle with plate ABC-123
- **When** security searches by plate at gate
- **Then** vehicle and owner unit displayed

### AC-RES-004: Move-Out
- **Given** active resident with outstanding invoices
- **When** move-out initiated
- **Then** warning displayed; admin can override with reason
- **And** all access revoked upon completion
- **And** status set to MOVED_OUT

---

## Module 3: Dashboard

### AC-DASH-001: Resident Dashboard
- **Given** logged-in resident
- **When** accessing dashboard
- **Then** widgets show: outstanding balance, upcoming visitors, recent announcements, quick actions
- **And** data loads within 2 seconds on 4G

### AC-DASH-002: Estate Manager Dashboard
- **Given** estate admin
- **When** accessing dashboard
- **Then** widgets show: occupancy rate, collection rate, open tickets, visitor count today
- **And** analytics reflect data ≤ 5 minutes old

### AC-DASH-003: Role-Based Widgets
- **Given** user with multiple roles
- **When** switching estate context
- **Then** dashboard widgets update to match role in selected estate

---

## Module 4: Visitor Management

### AC-VIS-001: QR Pass Generation
- **Given** resident creates visitor pass for "John Doe" valid 2 hours
- **When** pass generated
- **Then** unique QR code returned (PNG + deep link)
- **And** resident receives confirmation notification

### AC-VIS-002: Gate Scan — Valid Pass
- **Given** valid unexpired QR pass
- **When** security scans at gate
- **Then** green approval screen within 1 second
- **And** entry logged with timestamp
- **And** resident notified of check-in

### AC-VIS-003: Gate Scan — Expired Pass
- **Given** expired QR pass
- **When** scanned
- **Then** red denial with reason "Expired"
- **And** attempt logged

### AC-VIS-004: Blacklist
- **Given** phone +2348012345678 blacklisted
- **When** visitor pass created with that phone OR existing pass scanned
- **Then** access denied
- **And** security admin alerted

### AC-VIS-005: Delivery Pass
- **Given** resident creates delivery pass for "DHL"
- **When** courier arrives within validity window
- **Then** single-entry access granted
- **And** pass invalidated after entry

### AC-VIS-006: Visitor History
- **Given** estate admin
- **When** querying visitor logs for date range
- **Then** paginated results with entry/exit, gate, host unit
- **And** exportable to CSV

---

## Module 5: Security

### AC-SEC-001: SOS Alert
- **Given** resident triggers SOS
- **When** alert sent
- **Then** all on-duty security receive WebSocket + push within 2 seconds
- **And** SMS sent to security admin
- **And** alert includes unit, resident name, GPS if available

### AC-SEC-002: SOS Acknowledge/Resolve
- **Given** active SOS alert
- **When** security acknowledges
- **Then** status changes to ACKNOWLEDGED with responder ID
- **When** resolved with notes
- **Then** status RESOLVED; resident notified

### AC-SEC-003: Incident Report
- **Given** security creates incident with photos
- **When** submitted
- **Then** incident ID assigned; photos stored in S3
- **And** estate admin notified for severity ≥ HIGH

### AC-SEC-004: Patrol Logs
- **Given** scheduled patrol route with 5 checkpoints
- **When** security logs all checkpoints
- **Then** patrol marked COMPLETE
- **When** checkpoint missed beyond grace period
- **Then** alert sent to security admin

### AC-SEC-005: Emergency Broadcast
- **Given** security admin sends broadcast
- **When** message published
- **Then** all estate residents receive push + in-app within 60 seconds

---

## Module 6: Billing & Finance

### AC-BILL-001: Recurring Invoice Generation
- **Given** monthly service charge of ₦50,000 configured for Unit 12
- **When** billing cycle runs on 1st of month
- **Then** invoice generated with status ISSUED
- **And** resident notified via email + push

### AC-BILL-002: Online Payment
- **Given** outstanding invoice
- **When** resident pays via Paystack
- **Then** payment verified via webhook
- **And** invoice status updated to PAID
- **And** receipt generated

### AC-BILL-003: Payment Reminders
- **Given** invoice overdue by 7 days
- **When** reminder job runs
- **Then** email + SMS sent per estate configuration

### AC-BILL-004: Financial Reports
- **Given** finance admin requests monthly report
- **When** generated
- **Then** includes: total billed, collected, outstanding, aging breakdown
- **And** exportable PDF and CSV

### AC-BILL-005: Debt Restrictions
- **Given** resident debt exceeds estate threshold
- **When** attempting to create visitor pass
- **Then** blocked with message and payment link

---

## Module 7: Utility Payments

### AC-UTIL-001: Electricity Token Purchase
- **Given** resident with valid meter number
- **When** purchasing ₦10,000 electricity
- **Then** payment processed and token delivered
- **And** transaction recorded in utility history

### AC-UTIL-002: Consumption Analytics
- **Given** 6 months of utility data
- **When** resident views analytics
- **Then** chart shows monthly consumption trend
- **And** comparison to estate average displayed

---

## Module 8: Marketplace

### AC-MKT-001: Vendor Onboarding
- **Given** vendor application submitted
- **When** estate admin approves
- **Then** vendor status APPROVED; can list products
- **And** vendor dashboard accessible

### AC-MKT-002: Product Search
- **Given** 1000+ products indexed
- **When** searching "rice" with estate filter
- **Then** results returned within 300ms
- **And** only products from approved vendors in estate shown

### AC-MKT-003: Checkout
- **Given** cart with 3 items
- **When** checkout with valid payment
- **Then** order created; inventory decremented
- **And** vendor notified

### AC-MKT-004: Ratings
- **Given** completed order
- **When** resident submits 5-star rating with review
- **Then** product average rating updated
- **And** review visible on product page

---

## Module 9: Pharmacy

### AC-PHARM-001: Prescription Upload
- **Given** resident uploads prescription image
- **When** submitted
- **Then** file stored encrypted in S3
- **And** pharmacy partner notified for review

### AC-PHARM-002: Drug Reminders
- **Given** medication order with 30-day supply
- **When** reminder configured for 8 AM daily
- **Then** push notification sent at 8 AM daily

---

## Module 10: Healthcare

### AC-HEALTH-001: Hospital Locator
- **Given** resident location shared
- **When** searching hospitals within 10km
- **Then** results sorted by distance with map pins

### AC-HEALTH-002: Ambulance Request
- **Given** resident requests ambulance
- **When** submitted with location
- **Then** emergency contacts notified
- **And** request logged with timestamp

---

## Module 11: Facility Booking

### AC-FAC-001: Gym Booking
- **Given** gym slot available 6-7 PM
- **When** resident books slot
- **Then** booking confirmed; slot marked unavailable
- **And** confirmation notification sent

### AC-FAC-002: Capacity Enforcement
- **Given** tennis court max 4 bookings/day per resident
- **When** 5th booking attempted same day
- **Then** validation error returned

### AC-FAC-003: Paid Booking
- **Given** hall requires ₦100,000 deposit
- **When** booking initiated
- **Then** payment required before confirmation

---

## Module 12: Maintenance

### AC-MAINT-001: Ticket Creation
- **Given** resident submits ticket with 2 photos
- **When** created
- **Then** ticket ID assigned; photos in S3
- **And** estate admin notified

### AC-MAINT-002: SLA Tracking
- **Given** HIGH priority ticket (4-hour response SLA)
- **When** 4 hours pass without assignment
- **Then** SLA breach event fired; admin alerted

### AC-MAINT-003: Resolution Rating
- **Given** ticket RESOLVED
- **When** resident rates 4/5
- **Then** rating stored; technician average updated

---

## Module 13: Package Management

### AC-PKG-001: Package Logging
- **Given** security logs package for Unit 12
- **When** saved
- **Then** resident notified with pickup QR
- **And** package status AWAITING_PICKUP

### AC-PKG-002: QR Pickup
- **Given** valid pickup QR
- **When** scanned at pickup point
- **Then** status COLLECTED with timestamp

---

## Module 14: Parking

### AC-PARK-001: Resident Slot
- **Given** unit allocated slot P-12
- **When** resident views parking
- **Then** slot P-12 displayed with registered vehicles

### AC-PARK-002: Visitor Permit
- **Given** visitor pass with parking option
- **When** visitor arrives
- **Then** temporary permit valid for pass duration

---

## Module 15: Community

### AC-COMM-001: Feed Post
- **Given** resident creates post
- **When** published
- **Then** visible to estate residents in feed
- **And** WebSocket event broadcast

### AC-COMM-002: Announcements
- **Given** estate admin publishes announcement
- **When** saved
- **Then** pinned in feed; push to all residents

### AC-COMM-003: Polls
- **Given** poll with 3 options
- **When** resident votes
- **Then** vote recorded; results update in real-time
- **And** duplicate vote prevented

---

## Module 16: Transportation

### AC-TRANS-001: Ride Pre-Authorization
- **Given** resident shares expected Uber arrival
- **When** ride linked to visitor pass
- **Then** gate can verify plate against pass

---

## Module 17: Analytics

### AC-ANLYT-001: Executive Dashboard
- **Given** super admin
- **When** viewing platform analytics
- **Then** cross-estate revenue, user growth, active estates displayed
- **And** data refresh ≤ 15 minutes

### AC-ANLYT-002: Estate Performance
- **Given** estate admin
- **When** viewing occupancy analytics
- **Then** occupied/vacant units, trend over 12 months shown

---

## Module 18: AI Concierge

### AC-AI-001: FAQ with RAG
- **Given** estate FAQ document indexed
- **When** resident asks "What are gate hours?"
- **Then** accurate answer with citation to source document
- **And** response within 5 seconds

### AC-AI-002: Facility Booking via AI
- **Given** gym slot available tomorrow 7 AM
- **When** resident asks AI to book gym tomorrow morning
- **Then** booking confirmed and confirmation returned in chat

### AC-AI-003: Incident Reporting via AI
- **Given** resident describes security concern
- **When** AI processes intent
- **Then** maintenance/security ticket created with description
- **And** ticket ID returned to user

---

## Module 19: Predictive Maintenance

### AC-PRED-001: Failure Prediction
- **Given** equipment with declining performance metrics
- **When** prediction model runs
- **Then** alert generated if failure probability > 70% within 30 days
- **And** estate admin notified

---

## Cross-Cutting Acceptance Criteria

### AC-X-001: Multi-Tenant Isolation
- **Given** two estates A and B with identical unit numbers
- **When** user in Estate A queries units
- **Then** only Estate A units returned; zero leakage

### AC-X-002: Soft Delete
- **Given** entity soft-deleted
- **When** default API query
- **Then** entity not returned
- **When** admin queries with `include_deleted=true`
- **Then** entity returned with `deleted_at` populated

### AC-X-003: Audit Trail
- **Given** privileged action (role change, payment refund)
- **When** action performed
- **Then** immutable audit log entry with actor, timestamp, before/after state

### AC-X-004: GDPR/NDPR Data Export
- **Given** resident requests data export
- **When** processed within 30 days
- **Then** ZIP with all personal data delivered securely

### AC-X-005: API Documentation
- **Given** OpenAPI spec at `/api/v1/schema/`
- **When** accessed
- **Then** all endpoints documented with request/response schemas

### AC-X-006: Test Coverage
- **Given** full test suite
- **When** coverage report generated
- **Then** line coverage ≥ 90% across backend modules

### AC-X-007: Load Test
- **Given** 10,000 concurrent API requests
- **When** load test runs for 10 minutes
- **Then** p95 latency < 500ms; error rate < 0.1%

### AC-X-008: Dark/Light Mode
- **Given** user toggles theme
- **When** preference saved
- **Then** all pages render correctly in both modes
- **And** preference persists across sessions

---

## Sign-Off Checklist

| Module | Criteria Count | Status |
|--------|----------------|--------|
| Authentication | 7 | Pending |
| Resident Management | 4 | Pending |
| Dashboard | 3 | Pending |
| Visitor Management | 6 | Pending |
| Security | 5 | Pending |
| Billing & Finance | 5 | Pending |
| Utility Payments | 2 | Pending |
| Marketplace | 4 | Pending |
| Pharmacy | 2 | Pending |
| Healthcare | 2 | Pending |
| Facility Booking | 3 | Pending |
| Maintenance | 3 | Pending |
| Package Management | 2 | Pending |
| Parking | 2 | Pending |
| Community | 3 | Pending |
| Transportation | 1 | Pending |
| Analytics | 2 | Pending |
| AI Concierge | 3 | Pending |
| Predictive Maintenance | 1 | Pending |
| Cross-Cutting | 8 | Pending |
