"""Shared constants for EstateOS demo / QA seed data."""

DEMO_PASSWORD = "DemoPass12345"
DEMO_EMAIL_DOMAIN = "demo.estateos"
DEMO_MARKER = "estateos-demo-seed-v1"

DEMO_SUPERUSER = {
    "username": "superadmin",
    "email": f"superadmin@{DEMO_EMAIL_DOMAIN}",
    "first_name": "Platform",
    "last_name": "Super Admin",
}

PALM_GROVE_SLUG = "palm-grove-demo"
OAK_HEIGHTS_SLUG = "oak-heights-demo"

DEMO_ESTATE_SLUGS = (PALM_GROVE_SLUG, OAK_HEIGHTS_SLUG)

PALM_GROVE = {
    "name": "Palm Grove Demo Estate",
    "slug": PALM_GROVE_SLUG,
    "address_line1": "12 Palm Avenue",
    "city": "Lagos",
    "state": "Lagos",
    "country": "NG",
    "contact_email": f"contact@{PALM_GROVE_SLUG}.estateos",
    "contact_phone": "+2348010000001",
    "total_units": 24,
    "tier": "premium",
}

OAK_HEIGHTS = {
    "name": "Oak Heights Demo Estate",
    "slug": OAK_HEIGHTS_SLUG,
    "address_line1": "5 Oak Street",
    "city": "Abuja",
    "state": "FCT",
    "country": "NG",
    "contact_email": f"contact@{OAK_HEIGHTS_SLUG}.estateos",
    "contact_phone": "+2348010000002",
    "total_units": 8,
    "tier": "standard",
}

DEMO_PERMISSIONS = (
    ("residents.view", "View Residents", "residents"),
    ("residents.manage", "Manage Residents", "residents"),
    ("visitors.manage", "Manage Visitors", "visitors"),
    ("billing.view", "View Billing", "billing"),
    ("billing.manage", "Manage Billing", "billing"),
    ("security.view", "View Security", "security"),
    ("security.manage", "Manage Security", "security"),
    ("maintenance.view", "View Maintenance", "maintenance"),
    ("maintenance.manage", "Manage Maintenance", "maintenance"),
    ("facilities.manage", "Manage Facilities", "facilities"),
    ("marketplace.view", "View Marketplace", "marketplace"),
    ("analytics.view", "View Analytics", "analytics"),
)

ROLE_PERMISSION_CODES = {
    "estate_admin": [code for code, _, _ in DEMO_PERMISSIONS],
    "finance_admin": ["billing.view", "billing.manage", "residents.view", "analytics.view"],
    "security_admin": ["security.view", "security.manage", "visitors.manage", "residents.view"],
    "facility_admin": ["facilities.manage", "maintenance.view", "maintenance.manage"],
    "resident": ["residents.view", "billing.view", "marketplace.view"],
    "vendor": ["marketplace.view"],
    "technician": ["maintenance.view", "maintenance.manage"],
    "security_personnel": ["security.view", "visitors.manage"],
}
