"""Payment provider integration tests with mocked external APIs."""
import hashlib
import hmac
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from payments.providers import get_payment_provider
from payments.providers.base import PaymentInitRequest, RefundRequest
from payments.providers.flutterwave import FlutterwaveProvider
from payments.providers.paystack import PaystackProvider
from payments.providers.stripe import StripeProvider


@pytest.fixture
def payment_request():
    return PaymentInitRequest(
        amount=Decimal("5000.00"),
        currency="NGN",
        email="payer@test.estateos",
        reference="EST-PAY-001",
        callback_url="https://estateos.test/callback",
        description="Service charge payment",
    )


@pytest.mark.django_db
class TestPaystackProvider:
    @patch("payments.providers.paystack.requests.post")
    def test_initialize_payment_success(self, mock_post, payment_request):
        mock_post.return_value = MagicMock(
            json=lambda: {
                "status": True,
                "data": {
                    "authorization_url": "https://checkout.paystack.com/abc",
                    "access_code": "access_123",
                    "reference": "EST-PAY-001",
                },
            }
        )
        provider = PaystackProvider(secret_key="sk_test", public_key="pk_test")
        result = provider.initialize_payment(payment_request)
        assert result.success is True
        assert "checkout.paystack.com" in result.authorization_url

    @patch("payments.providers.paystack.requests.get")
    def test_verify_payment_success(self, mock_get):
        mock_get.return_value = MagicMock(
            json=lambda: {
                "status": True,
                "data": {
                    "status": "success",
                    "amount": 500000,
                    "currency": "NGN",
                    "reference": "EST-PAY-001",
                    "id": 999,
                    "paid_at": "2026-06-11T10:00:00Z",
                },
            }
        )
        provider = PaystackProvider(secret_key="sk_test")
        result = provider.verify_payment("EST-PAY-001")
        assert result.success is True
        assert result.amount == Decimal("5000.00")

    def test_webhook_signature_validation(self):
        provider = PaystackProvider(secret_key="sk_test")
        payload = b'{"event":"charge.success"}'
        signature = hmac.new(b"sk_test", payload, hashlib.sha512).hexdigest()
        assert provider.validate_webhook_signature(payload, signature) is True


@pytest.mark.django_db
class TestFlutterwaveProvider:
    @patch("payments.providers.flutterwave.requests.post")
    def test_initialize_payment_success(self, mock_post, payment_request):
        mock_post.return_value = MagicMock(
            json=lambda: {
                "status": "success",
                "data": {"link": "https://flutterwave.com/pay/abc", "id": 42},
            }
        )
        provider = FlutterwaveProvider(secret_key="flw_test")
        result = provider.initialize_payment(payment_request)
        assert result.success is True
        assert result.authorization_url.startswith("https://flutterwave.com")

    @patch("payments.providers.flutterwave.requests.get")
    def test_verify_payment_success(self, mock_get):
        mock_get.return_value = MagicMock(
            json=lambda: {
                "status": "success",
                "data": {
                    "status": "successful",
                    "amount": 5000,
                    "currency": "NGN",
                    "tx_ref": "EST-PAY-001",
                    "id": 42,
                    "created_at": "2026-06-11T10:00:00Z",
                },
            }
        )
        provider = FlutterwaveProvider(secret_key="flw_test")
        result = provider.verify_payment("EST-PAY-001")
        assert result.success is True

    @patch("payments.providers.flutterwave.requests.post")
    def test_refund_payment(self, mock_post):
        mock_post.return_value = MagicMock(
            json=lambda: {"status": "success", "data": {"id": 77}}
        )
        provider = FlutterwaveProvider(secret_key="flw_test")
        result = provider.refund_payment(RefundRequest(transaction_reference="42"))
        assert result.success is True


@pytest.mark.django_db
class TestStripeProvider:
    @patch("payments.providers.stripe.requests.post")
    def test_initialize_checkout_session(self, mock_post, payment_request):
        payment_request.currency = "USD"
        mock_post.return_value = MagicMock(
            json=lambda: {
                "id": "cs_test_123",
                "url": "https://checkout.stripe.com/pay/cs_test_123",
            }
        )
        provider = StripeProvider(secret_key="sk_test")
        result = provider.initialize_payment(payment_request)
        assert result.success is True
        assert "stripe.com" in result.authorization_url

    @patch("payments.providers.stripe.requests.get")
    def test_verify_checkout_session(self, mock_get):
        mock_get.return_value = MagicMock(
            json=lambda: {
                "data": [
                    {
                        "id": "cs_test_123",
                        "payment_status": "paid",
                        "amount_total": 500000,
                        "currency": "usd",
                    }
                ]
            }
        )
        provider = StripeProvider(secret_key="sk_test")
        result = provider.verify_payment("EST-PAY-001")
        assert result.success is True
        assert result.amount == Decimal("5000.00")


@pytest.mark.django_db
class TestProviderFactory:
    def test_get_paystack_provider(self):
        provider = get_payment_provider("paystack", secret_key="sk_test")
        assert isinstance(provider, PaystackProvider)

    def test_get_flutterwave_provider(self):
        provider = get_payment_provider("flutterwave", secret_key="flw_test")
        assert isinstance(provider, FlutterwaveProvider)

    def test_get_stripe_provider(self):
        provider = get_payment_provider("stripe", secret_key="sk_test")
        assert isinstance(provider, StripeProvider)

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown payment provider"):
            get_payment_provider("unknown")
