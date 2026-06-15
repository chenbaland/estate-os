"""End-to-end integration flows across EstateOS modules."""
import uuid
from decimal import Decimal

import pytest
from django.utils import timezone

from billing.models import Invoice, Payment
from marketplace.models import Order, Product
from residents.models import ResidentProfile
from visitors.models import Blacklist, VisitorLog, VisitorPass


@pytest.mark.django_db
@pytest.mark.integration
class TestResidentVisitorGateFlow:
    def test_onboarding_to_visitor_pass_to_gate_scan(self, user, estate, unit, admin_user):
        profile = ResidentProfile.objects.create(
            estate=estate,
            user=user,
            unit=unit,
            resident_type=ResidentProfile.ResidentType.OWNER,
            status=ResidentProfile.Status.PENDING,
        )
        profile.status = ResidentProfile.Status.ACTIVE
        profile.move_in_date = timezone.now().date()
        profile.is_primary = True
        profile.save()

        visitor_pass = VisitorPass.objects.create(
            estate=estate,
            host=profile,
            visitor_name="Delivery Agent",
            visitor_phone="+2348066666666",
            pass_type=VisitorPass.PassType.SINGLE,
            qr_code=f"QR-{uuid.uuid4().hex[:12]}",
            valid_until=timezone.now() + timezone.timedelta(hours=2),
            purpose="Package delivery",
        )

        Blacklist.objects.create(
            estate=estate,
            full_name="Blocked Visitor",
            phone="+2348077777777",
            reason=Blacklist.Reason.TRESPASS,
            description="Previously trespassed",
            reported_by=admin_user,
        )
        is_blacklisted = Blacklist.objects.filter(
            estate=estate,
            phone=visitor_pass.visitor_phone,
            is_active=True,
        ).exists()
        assert is_blacklisted is False

        VisitorLog.objects.create(
            estate=estate,
            visitor_pass=visitor_pass,
            visitor_name=visitor_pass.visitor_name,
            host=profile,
            direction=VisitorLog.Direction.ENTRY,
            verification_method=VisitorLog.VerificationMethod.QR,
            gate_name="Main Gate",
            verified_by=admin_user,
        )
        visitor_pass.entries_used = 1
        visitor_pass.status = VisitorPass.Status.USED
        visitor_pass.save()

        visitor_pass.refresh_from_db()
        assert visitor_pass.status == VisitorPass.Status.USED
        assert VisitorLog.objects.filter(visitor_pass=visitor_pass).count() == 1


@pytest.mark.django_db
@pytest.mark.integration
class TestInvoicePaymentFlow:
    def test_invoice_generation_to_payment(self, invoice, user, paystack_config):
        assert invoice.status == Invoice.Status.ISSUED
        assert invoice.balance_due == Decimal("50000.00")

        payment = Payment.objects.create(
            estate=invoice.estate,
            invoice=invoice,
            payer=user,
            reference=f"PAY-{uuid.uuid4().hex[:8]}",
            method=Payment.Method.CARD,
            status=Payment.Status.COMPLETED,
            amount=invoice.total_amount,
            provider=paystack_config.provider,
            provider_reference="PSK-INTEGRATION-001",
            paid_at=timezone.now(),
        )

        invoice.amount_paid = payment.amount
        invoice.status = Invoice.Status.PAID
        invoice.save()

        invoice.refresh_from_db()
        assert invoice.status == Invoice.Status.PAID
        assert invoice.balance_due == Decimal("0.00")
        assert Payment.objects.filter(invoice=invoice, status=Payment.Status.COMPLETED).exists()


@pytest.mark.django_db
@pytest.mark.integration
class TestMarketplaceOrderFlow:
    def test_product_to_order_to_delivery(self, estate, user, vendor, unit, product):
        order = Order.objects.create(
            estate=estate,
            order_number=f"ORD-{uuid.uuid4().hex[:8]}",
            user=user,
            vendor=vendor,
            unit=unit,
            status=Order.Status.PENDING,
            items=[
                {
                    "product_id": str(product.id),
                    "name": product.name,
                    "quantity": 1,
                    "unit_price": str(product.price),
                }
            ],
            subtotal=product.price,
            delivery_fee=Decimal("500.00"),
            total_amount=product.price + Decimal("500.00"),
            currency="NGN",
            delivery_address=f"Unit {unit.unit_number}",
        )

        product.stock_quantity -= 1
        product.save()

        order.status = Order.Status.CONFIRMED
        order.save()
        order.status = Order.Status.PREPARING
        order.save()
        order.status = Order.Status.OUT_FOR_DELIVERY
        order.save()
        order.status = Order.Status.DELIVERED
        order.delivered_at = timezone.now()
        order.payment_reference = f"PAY-{uuid.uuid4().hex[:8]}"
        order.save()

        order.refresh_from_db()
        product.refresh_from_db()
        assert order.status == Order.Status.DELIVERED
        assert order.delivered_at is not None
        assert product.stock_quantity == 99
