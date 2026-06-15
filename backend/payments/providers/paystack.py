"""
Paystack payment provider implementation.
"""
import hashlib
import hmac
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

logger = logging.getLogger("estateos.payments.paystack")

PAYSTACK_BASE_URL = "https://api.paystack.co"


class PaystackProvider(BasePaymentProvider):
    provider_name = "paystack"

    def __init__(
        self,
        secret_key: str = "",
        public_key: str = "",
        webhook_secret: str = "",
        **config,
    ):
        super().__init__(
            secret_key=secret_key or settings.PAYSTACK_SECRET_KEY,
            public_key=public_key or settings.PAYSTACK_PUBLIC_KEY,
            webhook_secret=webhook_secret,
            **config,
        )
        self.base_url = config.get("base_url", PAYSTACK_BASE_URL)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    def initialize_payment(self, request: PaymentInitRequest) -> PaymentInitResponse:
        payload = {
            "email": request.email,
            "amount": int(request.amount * 100),
            "currency": request.currency,
            "reference": request.reference,
            "callback_url": request.callback_url,
            "metadata": request.metadata,
        }
        try:
            response = requests.post(
                f"{self.base_url}/transaction/initialize",
                json=payload,
                headers=self._headers(),
                timeout=30,
            )
            data = response.json()
            if data.get("status") and data.get("data"):
                return PaymentInitResponse(
                    success=True,
                    reference=request.reference,
                    authorization_url=data["data"].get("authorization_url", ""),
                    access_code=data["data"].get("access_code", ""),
                    provider_reference=data["data"].get("reference", ""),
                    raw_response=data,
                )
            return PaymentInitResponse(
                success=False,
                reference=request.reference,
                error_message=data.get("message", "Payment initialization failed"),
                raw_response=data,
            )
        except requests.RequestException as exc:
            logger.exception("Paystack initialize failed: %s", exc)
            return PaymentInitResponse(
                success=False,
                reference=request.reference,
                error_message=str(exc),
            )

    def verify_payment(self, reference: str) -> PaymentVerifyResponse:
        try:
            response = requests.get(
                f"{self.base_url}/transaction/verify/{reference}",
                headers=self._headers(),
                timeout=30,
            )
            data = response.json()
            if data.get("status") and data.get("data"):
                txn = data["data"]
                return PaymentVerifyResponse(
                    success=txn.get("status") == "success",
                    status=txn.get("status", "failed"),
                    amount=Decimal(txn.get("amount", 0)) / 100,
                    currency=txn.get("currency", "NGN"),
                    reference=txn.get("reference", reference),
                    provider_reference=str(txn.get("id", "")),
                    paid_at=txn.get("paid_at"),
                    raw_response=data,
                )
            return PaymentVerifyResponse(
                success=False,
                status="failed",
                amount=Decimal("0"),
                currency="NGN",
                reference=reference,
                error_message=data.get("message", "Verification failed"),
                raw_response=data,
            )
        except requests.RequestException as exc:
            logger.exception("Paystack verify failed: %s", exc)
            return PaymentVerifyResponse(
                success=False,
                status="failed",
                amount=Decimal("0"),
                currency="NGN",
                reference=reference,
                error_message=str(exc),
            )

    def refund_payment(self, request: RefundRequest) -> RefundResponse:
        payload = {"transaction": request.transaction_reference}
        if request.amount:
            payload["amount"] = int(request.amount * 100)
        try:
            response = requests.post(
                f"{self.base_url}/refund",
                json=payload,
                headers=self._headers(),
                timeout=30,
            )
            data = response.json()
            if data.get("status"):
                return RefundResponse(
                    success=True,
                    refund_reference=str(data.get("data", {}).get("id", "")),
                    status="processed",
                    raw_response=data,
                )
            return RefundResponse(
                success=False,
                error_message=data.get("message", "Refund failed"),
                raw_response=data,
            )
        except requests.RequestException as exc:
            logger.exception("Paystack refund failed: %s", exc)
            return RefundResponse(success=False, error_message=str(exc))

    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        computed = hmac.new(
            self.secret_key.encode("utf-8"),
            payload,
            hashlib.sha512,
        ).hexdigest()
        return hmac.compare_digest(computed, signature)
