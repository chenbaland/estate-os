"""Shared pytest fixtures for EstateOS backend tests."""
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import MFADevice, Permission, Role, User, UserRole, UserSession
from billing.models import FeeType, Invoice, InvoiceLine
from estates.models import Block, Estate, Unit
from marketplace.models import Order, Product, Vendor
from payments.models import PaymentProviderConfig
from residents.models import FamilyMember, ResidentProfile, Vehicle


TEST_PASSWORD = "testpass12345"


def _auth_headers(client: APIClient, user: User, estate: Estate | None = None) -> APIClient:
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    if estate:
        client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
            HTTP_X_ESTATE_ID=str(estate.id),
        )
    return client


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def estate(db):
    return Estate.objects.create(
        name="Palm Grove Estate",
        slug="palm-grove",
        address_line1="12 Palm Avenue",
        city="Lagos",
        state="Lagos",
        country="NG",
        contact_email="admin@palmgrove.test",
        total_units=50,
    )


@pytest.fixture
def other_estate(db):
    return Estate.objects.create(
        name="Oak Heights",
        slug="oak-heights",
        address_line1="5 Oak Street",
        city="Abuja",
        state="FCT",
        country="NG",
        contact_email="admin@oakheights.test",
        total_units=30,
    )


@pytest.fixture
def block(estate):
    return Block.objects.create(
        estate=estate,
        name="Block A",
        code="A",
        floor_count=4,
        unit_count=10,
    )


@pytest.fixture
def unit(estate, block):
    return Unit.objects.create(
        estate=estate,
        block=block,
        unit_number="A-101",
        unit_type=Unit.UnitType.APARTMENT,
        occupancy_status=Unit.OccupancyStatus.VACANT,
        monthly_service_charge=Decimal("50000.00"),
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="resident1",
        email="resident1@test.estateos",
        password=TEST_PASSWORD,
        first_name="Ada",
        last_name="Okonkwo",
        phone="+2348012345678",
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="estateadmin",
        email="admin@test.estateos",
        password=TEST_PASSWORD,
        first_name="Estate",
        last_name="Admin",
        is_staff=True,
    )


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        username="superadmin",
        email="super@test.estateos",
        password=TEST_PASSWORD,
    )


@pytest.fixture
def superuser_client(api_client, superuser):
    return _auth_headers(api_client, superuser)


@pytest.fixture
def permission_view_residents(db):
    return Permission.objects.create(
        code="residents.view",
        name="View Residents",
        module="residents",
    )


@pytest.fixture
def permission_manage_visitors(db):
    return Permission.objects.create(
        code="visitors.manage",
        name="Manage Visitors",
        module="visitors",
    )


@pytest.fixture
def resident_role(estate, permission_view_residents):
    role = Role.objects.create(
        estate=estate,
        code=Role.RoleCode.RESIDENT,
        name="Resident",
        is_system_role=True,
    )
    role.permissions.add(permission_view_residents)
    return role


@pytest.fixture
def admin_role(estate, permission_view_residents, permission_manage_visitors):
    role = Role.objects.create(
        estate=estate,
        code=Role.RoleCode.ESTATE_ADMIN,
        name="Estate Admin",
        is_system_role=True,
        priority=10,
    )
    role.permissions.add(permission_view_residents, permission_manage_visitors)
    return role


@pytest.fixture
def resident(user, estate, unit, resident_role):
    UserRole.objects.create(user=user, role=resident_role, estate=estate)
    profile = ResidentProfile.objects.create(
        estate=estate,
        user=user,
        unit=unit,
        resident_type=ResidentProfile.ResidentType.OWNER,
        status=ResidentProfile.Status.ACTIVE,
        is_primary=True,
        move_in_date=timezone.now().date(),
    )
    unit.occupancy_status = Unit.OccupancyStatus.OCCUPIED
    unit.owner = user
    unit.save(update_fields=["occupancy_status", "owner", "updated_at"])
    return profile


@pytest.fixture
def authenticated_client(api_client, user, estate):
    return _auth_headers(api_client, user, estate)


@pytest.fixture
def admin_client(api_client, admin_user, estate, admin_role):
    UserRole.objects.create(user=admin_user, role=admin_role, estate=estate)
    return _auth_headers(api_client, admin_user, estate)


@pytest.fixture
def family_member(resident):
    return FamilyMember.objects.create(
        estate=resident.estate,
        primary_resident=resident,
        full_name="Chidi Okonkwo",
        relationship=FamilyMember.Relationship.CHILD,
        phone="+2348098765432",
        has_gate_access=True,
    )


@pytest.fixture
def vehicle(resident):
    return Vehicle.objects.create(
        estate=resident.estate,
        owner=resident,
        vehicle_type=Vehicle.VehicleType.CAR,
        make="Toyota",
        model="Camry",
        color="Black",
        license_plate="LAG-123-XY",
    )


@pytest.fixture
def fee_type(estate):
    return FeeType.objects.create(
        estate=estate,
        name="Monthly Service Charge",
        code="service_charge",
        amount=Decimal("50000.00"),
        frequency=FeeType.Frequency.MONTHLY,
    )


@pytest.fixture
def invoice(estate, unit, resident, fee_type):
    inv = Invoice.objects.create(
        estate=estate,
        invoice_number="INV-2026-0001",
        unit=unit,
        resident=resident,
        status=Invoice.Status.ISSUED,
        due_date=timezone.now().date() + timedelta(days=14),
        subtotal=Decimal("50000.00"),
        total_amount=Decimal("50000.00"),
        currency="NGN",
    )
    InvoiceLine.objects.create(
        estate=estate,
        invoice=inv,
        fee_type=fee_type,
        description="Service charge - June 2026",
        quantity=Decimal("1"),
        unit_price=Decimal("50000.00"),
        amount=Decimal("50000.00"),
    )
    return inv


@pytest.fixture
def paystack_config(estate):
    return PaymentProviderConfig.objects.create(
        estate=estate,
        provider=PaymentProviderConfig.Provider.PAYSTACK,
        is_default=True,
        is_active=True,
        public_key="pk_test_xxx",
        secret_key_encrypted="sk_test_xxx",
        supported_currencies=["NGN"],
        supported_methods=["card", "bank_transfer"],
    )


@pytest.fixture
def vendor(estate, user):
    return Vendor.objects.create(
        estate=estate,
        user=user,
        business_name="Fresh Mart",
        slug="fresh-mart",
        category="groceries",
        status=Vendor.Status.ACTIVE,
        phone="+2348011111111",
        email="vendor@test.estateos",
    )


@pytest.fixture
def product(estate, vendor):
    return Product.objects.create(
        estate=estate,
        vendor=vendor,
        name="Organic Eggs",
        slug="organic-eggs",
        category="dairy",
        price=Decimal("2500.00"),
        stock_quantity=100,
        status=Product.Status.ACTIVE,
    )


@pytest.fixture
def marketplace_order(estate, user, vendor, unit, product):
    return Order.objects.create(
        estate=estate,
        order_number="ORD-2026-0001",
        user=user,
        vendor=vendor,
        unit=unit,
        status=Order.Status.PENDING,
        items=[
            {
                "product_id": str(product.id),
                "name": product.name,
                "quantity": 2,
                "unit_price": str(product.price),
            }
        ],
        subtotal=Decimal("5000.00"),
        delivery_fee=Decimal("500.00"),
        total_amount=Decimal("5500.00"),
        currency="NGN",
        delivery_address="Unit A-101, Palm Grove",
    )


@pytest.fixture
def mfa_device(user):
    return MFADevice.objects.create(
        user=user,
        mfa_type=MFADevice.MFAType.TOTP,
        name="Authenticator",
        secret="JBSWY3DPEHPK3PXP",
        is_primary=True,
        is_verified=True,
    )


@pytest.fixture
def user_session(user, estate):
    return UserSession.objects.create(
        user=user,
        estate=estate,
        refresh_token_jti="test-jti-abc123",
        ip_address="127.0.0.1",
        user_agent="pytest-agent",
        is_active=True,
        expires_at=timezone.now() + timedelta(days=7),
    )
