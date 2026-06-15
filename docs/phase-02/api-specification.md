# EstateOS — API Specification

**Version:** 1.0.0  
**Base URL:** `https://api.estateos.app/api/v1/`  
**OpenAPI:** `/api/v1/schema/` (Swagger UI at `/api/docs/`)

---

## 1. API Design Standards

### 1.1 Versioning

- URL path versioning: `/api/v1/`, `/api/v2/` (future)
- Breaking changes require new version; v1 supported minimum 12 months after v2 release
- Deprecation header: `Sunset: Sat, 01 Jan 2028 00:00:00 GMT`

### 1.2 Authentication

```
Authorization: Bearer <access_token>
X-Estate-Id: <estate_uuid>          # Required for tenant-scoped endpoints
X-Idempotency-Key: <uuid>           # Required for POST payments/orders
```

### 1.3 Response Format

**Success:**
```json
{
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-06-11T10:00:00Z"
  }
}
```

**Paginated List:**
```json
{
  "data": [ ... ],
  "pagination": {
    "cursor": "eyJpZCI6...",
    "has_more": true,
    "count": 25
  }
}
```

**Error (RFC 7807):**
```json
{
  "type": "https://estateos.app/errors/validation",
  "title": "Validation Error",
  "status": 400,
  "detail": "Invalid input",
  "errors": [
    { "field": "email", "message": "Enter a valid email address." }
  ]
}
```

### 1.4 HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success (GET, PATCH) |
| 201 | Created (POST) |
| 204 | No content (DELETE) |
| 400 | Validation error |
| 401 | Unauthenticated |
| 403 | Forbidden (RBAC) |
| 404 | Not found |
| 409 | Conflict (duplicate) |
| 422 | Business rule violation |
| 429 | Rate limited |
| 500 | Server error |

---

## 2. Authentication Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login/` | Email/password login |
| POST | `/auth/logout/` | Revoke refresh token |
| POST | `/auth/token/refresh/` | Refresh access token |
| POST | `/auth/otp/request/` | Request phone OTP |
| POST | `/auth/otp/verify/` | Verify OTP, get tokens |
| GET | `/auth/oauth/{provider}/authorize/` | OAuth redirect |
| POST | `/auth/oauth/{provider}/callback/` | OAuth callback |
| POST | `/auth/register/` | User registration |
| POST | `/auth/password/reset/` | Request password reset |
| POST | `/auth/password/confirm/` | Confirm password reset |
| POST | `/auth/mfa/setup/` | Enable MFA |
| POST | `/auth/mfa/verify/` | Verify MFA code |
| POST | `/auth/mfa/disable/` | Disable MFA |
| GET | `/auth/sessions/` | List active sessions |
| DELETE | `/auth/sessions/{id}/` | Revoke session |
| GET | `/auth/devices/` | List registered devices |
| DELETE | `/auth/devices/{id}/` | Remove device |

---

## 3. Account & RBAC Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/accounts/me/` | Current user profile |
| PATCH | `/accounts/me/` | Update profile |
| GET | `/accounts/users/` | List users (admin) |
| POST | `/accounts/users/{id}/roles/` | Assign role |
| DELETE | `/accounts/users/{id}/roles/{role_id}/` | Remove role |
| GET | `/accounts/roles/` | List roles |
| GET | `/accounts/permissions/` | List permissions |

---

## 4. Estate Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/estates/` | List user's estates |
| POST | `/estates/` | Create estate (super admin) |
| GET | `/estates/{id}/` | Estate detail |
| PATCH | `/estates/{id}/` | Update estate |
| GET | `/estates/{id}/blocks/` | List blocks |
| POST | `/estates/{id}/blocks/` | Create block |
| GET | `/estates/{id}/units/` | List units |
| POST | `/estates/{id}/units/` | Create unit |
| GET | `/estates/{id}/units/{unit_id}/` | Unit detail |

---

## 5. Resident Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/residents/` | List residents |
| POST | `/residents/` | Create/invite resident |
| GET | `/residents/{id}/` | Resident profile |
| PATCH | `/residents/{id}/` | Update profile |
| POST | `/residents/{id}/move-out/` | Process move-out |
| GET | `/residents/{id}/family-members/` | List family |
| POST | `/residents/{id}/family-members/` | Add family member |
| GET | `/residents/{id}/vehicles/` | List vehicles |
| POST | `/residents/{id}/vehicles/` | Register vehicle |
| GET | `/residents/{id}/domestic-staff/` | List staff |
| POST | `/residents/{id}/domestic-staff/` | Register staff |

---

## 6. Visitor Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/visitors/passes/` | List passes |
| POST | `/visitors/passes/` | Create pass |
| GET | `/visitors/passes/{id}/` | Pass detail |
| DELETE | `/visitors/passes/{id}/` | Revoke pass |
| GET | `/visitors/passes/{id}/qr/` | Get QR code image |
| POST | `/visitors/scan/` | Gate scan (security) |
| GET | `/visitors/logs/` | Visitor history |
| GET | `/visitors/blacklist/` | List blacklist |
| POST | `/visitors/blacklist/` | Add to blacklist |
| DELETE | `/visitors/blacklist/{id}/` | Remove from blacklist |

---

## 7. Security Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/security/incidents/` | List incidents |
| POST | `/security/incidents/` | Report incident |
| PATCH | `/security/incidents/{id}/` | Update incident |
| GET | `/security/patrols/` | Patrol logs |
| POST | `/security/patrols/` | Log patrol checkpoint |
| POST | `/security/sos/` | Trigger SOS |
| PATCH | `/security/sos/{id}/` | Acknowledge/resolve SOS |
| POST | `/security/broadcasts/` | Emergency broadcast |

---

## 8. Billing Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/billing/fee-types/` | List fee types |
| POST | `/billing/fee-types/` | Create fee type |
| GET | `/billing/invoices/` | List invoices |
| GET | `/billing/invoices/{id}/` | Invoice detail |
| POST | `/billing/invoices/generate/` | Generate recurring invoices |
| POST | `/billing/invoices/{id}/pay/` | Initiate payment |
| GET | `/billing/payments/` | Payment history |
| GET | `/billing/reports/` | Financial reports |
| GET | `/billing/debt/` | Debt management |

---

## 9. Utility Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/utilities/accounts/` | Utility accounts |
| POST | `/utilities/purchase/` | Purchase utility (electricity, airtime, etc.) |
| GET | `/utilities/transactions/` | Transaction history |
| GET | `/utilities/analytics/` | Consumption analytics |

---

## 10. Marketplace Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/marketplace/vendors/` | List vendors |
| POST | `/marketplace/vendors/apply/` | Vendor application |
| GET | `/marketplace/products/` | Search products |
| POST | `/marketplace/products/` | Create product (vendor) |
| GET | `/marketplace/cart/` | Get cart |
| POST | `/marketplace/cart/items/` | Add to cart |
| POST | `/marketplace/orders/` | Place order |
| GET | `/marketplace/orders/{id}/` | Order detail |
| POST | `/marketplace/orders/{id}/review/` | Submit review |

---

## 11. Module Endpoints (Summary)

| Module | Base Path | Key Operations |
|--------|-----------|----------------|
| Pharmacy | `/pharmacy/` | prescriptions, orders, reminders |
| Healthcare | `/healthcare/` | hospitals, appointments, ambulance |
| Facilities | `/facilities/` | list, bookings, availability |
| Maintenance | `/maintenance/` | tickets, comments, SLA |
| Packages | `/packages/` | log, pickup, tracking |
| Parking | `/parking/` | slots, permits, EV sessions |
| Community | `/community/` | posts, polls, announcements, groups, messages |
| Transportation | `/transportation/` | ride requests, verification |
| Analytics | `/analytics/` | dashboards, metrics, exports |
| AI | `/ai/` | chat, documents, predictions |
| Notifications | `/notifications/` | list, preferences, mark read |
| Payments | `/payments/webhooks/{provider}/` | Provider webhooks |

---

## 12. WebSocket API

**Connection:** `wss://api.estateos.app/ws/v1/{channel}/?token=<jwt>`

### 12.1 Channels

| Channel | Path | Events |
|---------|------|--------|
| Notifications | `/ws/v1/notifications/` | `notification.new`, `notification.read` |
| Security | `/ws/v1/security/{estate_id}/` | `sos.triggered`, `sos.acknowledged`, `incident.new` |
| Gate | `/ws/v1/gate/{gate_id}/` | `scan.result`, `scan.pending` |
| Chat | `/ws/v1/chat/{conversation_id}/` | `message.new`, `message.read`, `typing` |
| Community | `/ws/v1/community/{estate_id}/` | `post.new`, `poll.updated` |

### 12.2 Message Format

```json
{
  "type": "notification.new",
  "payload": {
    "id": "uuid",
    "title": "Visitor Arrived",
    "body": "John Doe has checked in at Main Gate",
    "created_at": "2026-06-11T10:00:00Z"
  }
}
```

### 12.3 Client → Server

```json
{
  "action": "mark_read",
  "notification_id": "uuid"
}
```

---

## 13. Rate Limiting

| Endpoint Group | Limit | Window |
|----------------|-------|--------|
| Auth endpoints | 20 req | 1 min / IP |
| API (authenticated) | 100 req | 1 min / user |
| Gate scan | 60 req | 1 min / device |
| AI chat | 30 req | 1 min / user |
| Webhooks | 1000 req | 1 min / provider IP |

Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## 14. Webhook Specifications

### 14.1 Payment Webhooks

```
POST /api/v1/payments/webhooks/paystack/
POST /api/v1/payments/webhooks/flutterwave/
POST /api/v1/payments/webhooks/stripe/
```

Signature verification required. Idempotent processing via `reference` field.

### 14.2 Event Payload (Paystack example)

```json
{
  "event": "charge.success",
  "data": {
    "reference": "EST-20260611-ABC123",
    "amount": 5000000,
    "currency": "NGN",
    "status": "success"
  }
}
```

---

## 15. File Upload

```
POST /api/v1/uploads/
Content-Type: multipart/form-data

Response:
{
  "data": {
    "upload_url": "https://s3.../presigned",
    "file_key": "estate-id/module/entity-id/file.jpg",
    "expires_at": "2026-06-11T10:15:00Z"
  }
}
```

Direct-to-S3 upload via pre-signed URL. Confirm upload: `POST /api/v1/uploads/confirm/`

---

## 16. Search API

```
GET /api/v1/search/?q=rice&type=product&estate_id=uuid
```

Types: `product`, `resident` (admin), `hospital`, `document`

Powered by Elasticsearch. Falls back to DB for single-entity lookups.

---

## 17. GDPR/NDPR Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/compliance/data-export/` | Request data export |
| GET | `/compliance/data-export/{id}/` | Export status/download |
| POST | `/compliance/data-deletion/` | Request account deletion |
| GET | `/compliance/consent/` | List consent records |
| POST | `/compliance/consent/` | Update consent |

---

## 18. Health & Metrics

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health/` | Health check (DB, Redis, RabbitMQ) |
| GET | `/metrics/` | Prometheus metrics (internal) |

---

## 19. Error Code Catalog

| Code | HTTP | Description |
|------|------|-------------|
| `AUTH_INVALID_CREDENTIALS` | 401 | Wrong email/password |
| `AUTH_MFA_REQUIRED` | 403 | MFA challenge needed |
| `AUTH_ACCOUNT_LOCKED` | 403 | Too many failed attempts |
| `TENANT_NOT_FOUND` | 404 | Invalid estate context |
| `TENANT_ACCESS_DENIED` | 403 | Cross-tenant access attempt |
| `VISITOR_PASS_EXPIRED` | 422 | Pass no longer valid |
| `VISITOR_BLACKLISTED` | 422 | Visitor on blacklist |
| `BILLING_DEBT_RESTRICTION` | 422 | Action blocked due to debt |
| `FACILITY_FULLY_BOOKED` | 422 | No available slots |
| `PAYMENT_FAILED` | 422 | Payment provider error |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

---

## 20. Full OpenAPI Specification

See [openapi.yaml](./openapi.yaml) for complete machine-readable specification.
