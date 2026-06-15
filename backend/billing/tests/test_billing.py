"""Tests for the billing module."""
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from accounts.models import User
from billing.models import DebtRecord, FeeType, Invoice, Payment
from estates.models import Estate, Unit
from residents.models import ResidentProfile


@pytest.fixture
def estate(db):
    return Estate.objects.create(
        name="Billing Estate",
        slug="billing-estate",
        total_units=5,
        is_active=True,
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email="billingadmin@test.com",
        username="billingadmin",
        password="adminpass123!",
    )


@pytest.fixture
def unit(db, estate):
    return Unit.objects.create(estate=estate, unit_number="B1", unit_type="apartment", is_active=True)


@pytest.fixture
def resident_user(db):
    return User.objects.create_user(
        email="billingresident@test.com",
        username="billingresident",
        password="respass123!",
    )


@pytest.fixture
def resident_profile(db, resident_user, estate, unit):
    return ResidentProfile.objects.create(
        user=resident_user,
        estate=estate,
        unit=unit,
        resident_type=ResidentProfile.ResidentType.OWNER,
        status=ResidentProfile.Status.ACTIVE,
    )


@pytest.fixture
def invoice(db, estate, unit, resident_profile):
    inv = Invoice.objects.create(
        estate=estate,
        unit=unit,
        resident=resident_profile,
        invoice_number="INV-0001",
        status=Invoice.Status.ISSUED,
        due_date="2026-12-31",
        subtotal=Decimal("50000.00"),
        total_amount=Decimal("50000.00"),
        amount_paid=Decimal("0.00"),
        currency="NGN",
    )
    return inv


@pytest.fixture
def auth_client(admin_user, estate):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    client.credentials(HTTP_X_ESTATE_ID=str(estate.id))
    return client


@pytest.mark.django_db
class TestFeeType:
    def test_create_fee_type(self, auth_client):
        response = auth_client.post(
            "/api/v1/billing/fee-types/",
            data={"name": "Service Charge", "code": "SC001", "amount": "5000.00", "frequency": "monthly"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["code"] == "SC001"

    def test_list_fee_types(self, auth_client, estate):
        FeeType.objects.create(estate=estate, name="Maintenance", code="MAINT", amount=Decimal("2000"))
        response = auth_client.get("/api/v1/billing/fee-types/")
        assert response.status_code == 200
        assert len(response.json()["results"]) >= 1


@pytest.mark.django_db
class TestInvoicePay:
    def test_full_payment_marks_invoice_paid(self, auth_client, invoice):
        response = auth_client.post(
            f"/api/v1/billing/invoices/{invoice.id}/pay/",
            data={"method": "bank_transfer"},
            format="json",
        )
        assert response.status_code == 201
        invoice.refresh_from_db()
        assert invoice.status == Invoice.Status.PAID
        assert invoice.amount_paid == Decimal("50000.00")

    def test_partial_payment_marks_invoice_partial(self, auth_client, invoice):
        response = auth_client.post(
            f"/api/v1/billing/invoices/{invoice.id}/pay/",
            data={"method": "bank_transfer", "amount": "20000.00"},
            format="json",
        )
        assert response.status_code == 201
        invoice.refresh_from_db()
        assert invoice.status == Invoice.Status.PARTIAL
        assert invoice.amount_paid == Decimal("20000.00")

    def test_payment_cannot_exceed_balance_due(self, auth_client, invoice):
        """Overpayment should be capped at balance_due."""
        response = auth_client.post(
            f"/api/v1/billing/invoices/{invoice.id}/pay/",
            data={"method": "bank_transfer", "amount": "99999.00"},
            format="json",
        )
        assert response.status_code == 201
        invoice.refresh_from_db()
        # Should be capped at 50000 (the balance due)
        assert invoice.amount_paid == Decimal("50000.00")
        assert invoice.status == Invoice.Status.PAID

    def test_pay_already_paid_invoice_rejected(self, auth_client, estate, unit, resident_profile):
        paid_inv = Invoice.objects.create(
            estate=estate,
            unit=unit,
            resident=resident_profile,
            invoice_number="INV-PAID",
            status=Invoice.Status.PAID,
            due_date="2026-12-31",
            total_amount=Decimal("10000.00"),
            amount_paid=Decimal("10000.00"),
            currency="NGN",
        )
        response = auth_client.post(
            f"/api/v1/billing/invoices/{paid_inv.id}/pay/",
            data={"method": "bank_transfer"},
            format="json",
        )
        assert response.status_code == 400

    def test_payment_creates_payment_record(self, auth_client, invoice):
        before = Payment.objects.count()
        auth_client.post(
            f"/api/v1/billing/invoices/{invoice.id}/pay/",
            data={"method": "card"},
            format="json",
        )
        assert Payment.objects.count() == before + 1

    def test_payment_reference_is_unique(self, auth_client, invoice, estate, unit, resident_profile):
        auth_client.post(
            f"/api/v1/billing/invoices/{invoice.id}/pay/",
            data={"method": "bank_transfer", "amount": "10000.00"},
            format="json",
        )
        inv2 = Invoice.objects.create(
            estate=estate,
            unit=unit,
            resident=resident_profile,
            invoice_number="INV-0002",
            status=Invoice.Status.ISSUED,
            due_date="2026-12-31",
            total_amount=Decimal("20000.00"),
            amount_paid=Decimal("0.00"),
            currency="NGN",
        )
        auth_client.post(
            f"/api/v1/billing/invoices/{inv2.id}/pay/",
            data={"method": "bank_transfer", "amount": "10000.00"},
            format="json",
        )
        refs = list(Payment.objects.values_list("reference", flat=True))
        assert len(refs) == len(set(refs))  # All references are unique

    def test_zero_amount_payment_rejected(self, auth_client, invoice):
        response = auth_client.post(
            f"/api/v1/billing/invoices/{invoice.id}/pay/",
            data={"method": "bank_transfer", "amount": "0.00"},
            format="json",
        )
        assert response.status_code == 400

    def test_list_invoices(self, auth_client, invoice):
        response = auth_client.get("/api/v1/billing/invoices/")
        assert response.status_code == 200
        assert len(response.json()["results"]) >= 1

    def test_list_payments(self, auth_client):
        response = auth_client.get("/api/v1/billing/payments/")
        assert response.status_code == 200
