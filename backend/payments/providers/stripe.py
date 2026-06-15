"""
Stripe payment provider implementation.
"""
import logging
from decimal import Decimal

import requests
from django.conf import settings

from payments.providers.base import (
    BasePaymentProvider,
    PaymentInitRequest,
    PaymentInitResponse,
    PaymentVerifyResponse,
    RefundRequest,
    RefundResponse,
)

logger = logging.getLogger("estateos.payments.stripe")

STRIPE_BASE_URL = "https://api.stripe.com/v1"


class StripeProvider(BasePaymentProvider):
    provider_name = "stripe"

    def __init__(
        self,
        secret_key: str = "",
        public_key: str = "",
        webhook_secret: str = "",
        **config,
    ):
        super().__init__(
            secret_key=secret_key or settings.STRIPE_SECRET_KEY,
            public_key=public_key or settings.STRIPE_PUBLIC_KEY,
            webhook_secret=webhook_secret or settings.STRIPE_WEBHOOK_SECRET,
            **config,
        )
        self.base_url = config.get("base_url", STRIPE_BASE_URL)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def initialize_payment(self, request: PaymentInitRequest) -> PaymentInitResponse:
        payload = {
            "mode": "payment",
            "success_url": request.callback_url or "https://estateos.app/payment/success",
            "cancel_url": request.callback_url or "https://estateos.app/payment/cancel",
            "client_reference_id": request.reference,
            "line_items[0][price_data][currency]": request.currency.lower(),
            "line_items[0][price_data][product_data][name]": request.description or "EstateOS Payment",
            "line_items[0][price_data][unit_amount]": int(request.amount * 100),
            "line_items[0][quantity]": 1,
            "customer_email": request.email,
            "metadata[reference]": request.reference,
        }
        try:
            response = requests.post(
                f"{self.base_url}/checkout/sessions",
                data=payload,
                headers=self._headers(),
                timeout=30,
            )
            data = response.json()
            if data.get("url"):
                return PaymentInitResponse(
                    success=True,
                    reference=request.reference,
                    authorization_url=data["url"],
                    provider_reference=data.get("id", ""),
                    raw_response=data,
                )
            return PaymentInitResponse(
                success=False,
                reference=request.reference,
                error_message=data.get("error", {}).get("message", "Payment initialization failed"),
                raw_response=data,
            )
        except requests.RequestException as exc:
            logger.exception("Stripe initialize failed: %s", exc)
            return PaymentInitResponse(
                success=False,
                reference=request.reference,
                error_message=str(exc),
            )

    def verify_payment(self, reference: str) -> PaymentVerifyResponse:
        try:
            response = requests.get(
                f"{self.base_url}/checkout/sessions",
                params={"client_reference_id": reference},
                headers=self._headers(),
                timeout=30,
            )
            data = response.json()
            sessions = data.get("data", [])
            if sessions:
                session = sessions[0]
                amount = Decimal(session.get("amount_total", 0)) / 100
                return PaymentVerifyResponse(
                    success=session.get("payment_status") == "paid",
                    status=session.get("payment_status", "unpaid"),
                    amount=amount,
                    currency=session.get("currency", "usd").upper(),
                    reference=reference,
                    provider_reference=session.get("id", ""),
                    raw_response=data,
                )
            return PaymentVerifyResponse(
                success=False,
                status="failed",
                amount=Decimal("0"),
                currency="USD",
                reference=reference,
                error_message="Session not found",
                raw_response=data,
            )
        except requests.RequestException as exc:
            logger.exception("Stripe verify failed: %s", exc)
            return PaymentVerifyResponse(
                success=False,
                status="failed",
                amount=Decimal("0"),
                currency="USD",
                reference=reference,
                error_message=str(exc),
            )

    def refund_payment(self, request: RefundRequest) -> RefundResponse:
        payload = {"payment_intent": request.transaction_reference}
        if request.amount:
            payload["amount"] = int(request.amount * 100)
        try:
            response = requests.post(
                f"{self.base_url}/refunds",
                data=payload,
                headers=self._headers(),
                timeout=30,
            )
            data = response.json()
            if data.get("status") in ("succeeded", "pending"):
                return RefundResponse(
                    success=True,
                    refund_reference=data.get("id", ""),
                    status=data.get("status", ""),
                    raw_response=data,
                )
            return RefundResponse(
                success=False,
                error_message=data.get("error", {}).get("message", "Refund failed"),
                raw_response=data,
            )
        except requests.RequestException as exc:
            logger.exception("Stripe refund failed: %s", exc)
            return RefundResponse(success=False, error_message=str(exc))

    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        import hmac
        import hashlib
        import time

        if not self.webhook_secret:
            return False
        try:
            elements = dict(item.split("=", 1) for item in signature.split(","))
            timestamp = elements.get("t", "")
            v1_sig = elements.get("v1", "")
            signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
            expected = hmac.new(
                self.webhook_secret.encode("utf-8"),
                signed_payload.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            if abs(time.time() - int(timestamp)) > 300:
                return False
            return hmac.compare_digest(expected, v1_sig)
        except (ValueError, KeyError):
            return False
