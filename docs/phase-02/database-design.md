# EstateOS — Database Design

**Version:** 1.0.0  
**DBMS:** PostgreSQL 16 with pgvector extension

---

## 1. Design Principles

| Principle | Implementation |
|-----------|----------------|
| Primary keys | UUID v4 (`gen_random_uuid()`) |
| Timestamps | `created_at`, `updated_at` (auto-managed) |
| Soft deletes | `deleted_at` nullable timestamp |
| Tenancy | `estate_id` FK on all tenant-scoped tables |
| Audit | Separate `audit_logs` table (append-only) |
| Naming | snake_case tables and columns |
| Constraints | CHECK constraints for enums; FK with ON DELETE PROTECT for financial records |

---

## 2. Schema Overview

### 2.1 Platform Tables

```sql
-- accounts_user (custom user model)
CREATE TABLE accounts_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_user_email ON accounts_user(email);
CREATE INDEX idx_user_phone ON accounts_user(phone) WHERE phone IS NOT NULL;
```

### 2.2 Estate Tables

```sql
CREATE TABLE estates_estate (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    country VARCHAR(2) NOT NULL DEFAULT 'NG',
    address TEXT,
    timezone VARCHAR(50) DEFAULT 'Africa/Lagos',
    settings JSONB DEFAULT '{}',
    subscription_tier VARCHAR(50) DEFAULT 'standard',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE estates_block (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estate_id UUID NOT NULL REFERENCES estates_estate(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    UNIQUE(estate_id, name)
);

CREATE TABLE estates_unit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estate_id UUID NOT NULL REFERENCES estates_estate(id),
    block_id UUID REFERENCES estates_block(id),
    unit_number VARCHAR(50) NOT NULL,
    unit_type VARCHAR(50) DEFAULT 'apartment',
    floor INTEGER,
    bedrooms INTEGER,
    status VARCHAR(20) DEFAULT 'vacant'
        CHECK (status IN ('vacant', 'occupied', 'maintenance')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    UNIQUE(estate_id, unit_number)
);

CREATE INDEX idx_unit_estate_status ON estates_unit(estate_id, status)
    WHERE deleted_at IS NULL;
```

### 2.3 RBAC Tables

```sql
CREATE TABLE accounts_role (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE accounts_permission (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codename VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    module VARCHAR(50) NOT NULL
);

CREATE TABLE accounts_user_role (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES accounts_user(id),
    role_id UUID NOT NULL REFERENCES accounts_role(id),
    estate_id UUID REFERENCES estates_estate(id),
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    assigned_by_id UUID REFERENCES accounts_user(id),
    UNIQUE(user_id, role_id, estate_id)
);

CREATE INDEX idx_user_role_estate ON accounts_user_role(user_id, estate_id);
```

---

## 3. Module Schemas (Key Tables)

### 3.1 Visitors

```sql
CREATE TABLE visitors_visitor_pass (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estate_id UUID NOT NULL REFERENCES estates_estate(id),
    resident_id UUID NOT NULL REFERENCES residents_resident_profile(id),
    pass_type VARCHAR(20) NOT NULL
        CHECK (pass_type IN ('qr', 'otp', 'delivery', 'recurring')),
    visitor_name VARCHAR(255) NOT NULL,
    visitor_phone VARCHAR(20),
    visitor_email VARCHAR(255),
    vehicle_plate VARCHAR(20),
    qr_code VARCHAR(255) UNIQUE NOT NULL,
    otp_code VARCHAR(6),
    valid_from TIMESTAMPTZ NOT NULL,
    valid_until TIMESTAMPTZ NOT NULL,
    max_entries INTEGER DEFAULT 1,
    entries_used INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active'
        CHECK (status IN ('active', 'used', 'expired', 'revoked')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX idx_visitor_pass_qr ON visitors_visitor_pass(qr_code);
CREATE INDEX idx_visitor_pass_estate_status ON visitors_visitor_pass(estate_id, status, valid_until)
    WHERE deleted_at IS NULL;
CREATE INDEX idx_visitor_pass_resident ON visitors_visitor_pass(resident_id, created_at DESC);

CREATE TABLE visitors_visitor_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estate_id UUID NOT NULL,
    pass_id UUID NOT NULL REFERENCES visitors_visitor_pass(id),
    gate_id VARCHAR(50),
    action VARCHAR(20) NOT NULL CHECK (action IN ('entry', 'exit', 'denied')),
    scanned_by_id UUID REFERENCES accounts_user(id),
    denial_reason VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (created_at);
```

### 3.2 Billing

```sql
CREATE TABLE billing_invoice (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estate_id UUID NOT NULL REFERENCES estates_estate(id),
    unit_id UUID NOT NULL REFERENCES estates_unit(id),
    resident_id UUID REFERENCES residents_resident_profile(id),
    invoice_number VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft'
        CHECK (status IN ('draft','issued','partially_paid','paid','overdue','written_off')),
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    amount_paid DECIMAL(12,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'NGN',
    due_date DATE NOT NULL,
    issued_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    UNIQUE(estate_id, invoice_number)
);

CREATE INDEX idx_invoice_estate_status_due ON billing_invoice(estate_id, status, due_date)
    WHERE deleted_at IS NULL;
CREATE INDEX idx_invoice_unit ON billing_invoice(unit_id, created_at DESC);
```

### 3.3 Marketplace

```sql
CREATE TABLE marketplace_product (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estate_id UUID NOT NULL REFERENCES estates_estate(id),
    vendor_id UUID NOT NULL REFERENCES marketplace_vendor(id),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'NGN',
    category VARCHAR(100),
    stock_quantity INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    average_rating DECIMAL(3,2) DEFAULT 0,
    review_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    UNIQUE(estate_id, vendor_id, slug)
);

CREATE INDEX idx_product_estate_category ON marketplace_product(estate_id, category, is_active)
    WHERE deleted_at IS NULL;
CREATE INDEX idx_product_vendor ON marketplace_product(vendor_id);
```

### 3.4 AI / RAG

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE ai_document (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estate_id UUID NOT NULL REFERENCES estates_estate(id),
    title VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    content_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending','processing','indexed','failed')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE ai_embedding (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estate_id UUID NOT NULL REFERENCES estates_estate(id),
    document_id UUID NOT NULL REFERENCES ai_document(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_embedding_estate ON ai_embedding(estate_id);
CREATE INDEX idx_embedding_vector ON ai_embedding
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## 4. Audit Tables

```sql
CREATE TABLE core_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estate_id UUID REFERENCES estates_estate(id),
    actor_id UUID REFERENCES accounts_user(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    before_state JSONB,
    after_state JSONB,
    ip_address INET,
    user_agent TEXT,
    trace_id VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
) PARTITION BY RANGE (created_at);

-- Monthly partitions created by management command
CREATE TABLE core_audit_log_2026_06 PARTITION OF core_audit_log
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
```

**Audited actions:** role changes, payment refunds, blacklist additions, invoice write-offs, data exports, super admin cross-tenant access.

---

## 5. Index Strategy

### 5.1 Composite Indexes (Tenant-Scoped Queries)

| Table | Index | Query Pattern |
|-------|-------|---------------|
| All tenant tables | `(estate_id, created_at DESC)` | List views |
| `residents_resident_profile` | `(estate_id, status)` | Active residents |
| `billing_invoice` | `(estate_id, status, due_date)` | Overdue invoices |
| `maintenance_ticket` | `(estate_id, status, priority)` | Open tickets |
| `security_sos_alert` | `(estate_id, status, created_at DESC)` | Active SOS |
| `community_post` | `(estate_id, created_at DESC)` | Feed pagination |

### 5.2 Unique Indexes

| Table | Index | Purpose |
|-------|-------|---------|
| `visitors_visitor_pass` | `qr_code` | Gate scan lookup |
| `billing_invoice` | `(estate_id, invoice_number)` | Invoice reference |
| `estates_unit` | `(estate_id, unit_number)` | Unit identity |
| `accounts_user` | `email`, `phone` | Login lookup |

### 5.3 Partial Indexes

```sql
-- Active records only (soft delete optimization)
CREATE INDEX idx_active_residents ON residents_resident_profile(estate_id, unit_id)
    WHERE deleted_at IS NULL AND status = 'active';

CREATE INDEX idx_active_passes ON visitors_visitor_pass(estate_id, valid_until)
    WHERE deleted_at IS NULL AND status = 'active';
```

---

## 6. Partition Strategy

### 6.1 Partitioned Tables

| Table | Strategy | Retention |
|-------|----------|-----------|
| `core_audit_log` | RANGE (monthly) | 7 years |
| `visitors_visitor_log` | RANGE (monthly) | 2 years |
| `analytics_metric_snapshot` | RANGE (monthly) | 3 years |
| `notifications_notification` | RANGE (monthly) | 1 year (read), archive older |

### 6.2 Partition Management

Celery Beat task runs monthly:
1. Create next month's partition
2. Detach partitions older than retention
3. Archive to S3 (Parquet) before drop

```sql
-- Automated via Django management command: manage_partitions
CREATE TABLE visitors_visitor_log_2026_07 PARTITION OF visitors_visitor_log
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
```

---

## 7. Soft Delete Implementation

All business entities extend `SoftDeleteModel`:

```python
class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)
```

Default manager returns `.alive()` only. Admin views can access `.dead()` with audit.

---

## 8. Data Encryption

| Data Type | Method |
|-----------|--------|
| Passwords | Argon2/bcrypt via Django |
| MFA secrets | Fernet symmetric encryption |
| Medical records | Field-level AES-256-GCM |
| Payment tokens | Never stored; provider references only |
| Refresh tokens | SHA-256 hashed in DB |

---

## 9. Migration Strategy

- Django migrations per app
- Zero-downtime: additive migrations first, backfill, then constraint
- Large table migrations use `CONCURRENTLY` index creation
- pgvector extension enabled in initial migration

---

## 10. Connection Pooling

Production configuration:
- PgBouncer in transaction pooling mode
- Django `CONN_MAX_AGE = 0` (delegate to PgBouncer)
- Max connections: 100 per API instance, 500 pool size

---

## 11. Backup & Recovery

| Component | Strategy |
|-----------|----------|
| RDS | Automated daily snapshots, 35-day retention |
| Point-in-time | 5-minute granularity |
| S3 | Versioning enabled, cross-region replication |
| Redis | AOF persistence, daily snapshots |
