"""
Flutterwave payment provider implementation.
"""
import hashlib
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

logger = logging.getLogger("estateos.payments.flutterwave")

FLUTTERWAVE_BASE_URL = "https://api.flutterwave.com/v3"


class FlutterwaveProvider(BasePaymentProvider):
    provider_name = "flutterwave"

    def __init__(
        self,
        secret_key: str = "",
        public_key: str = "",
        webhook_secret: str = "",
        **config,
    ):
        super().__init__(
            secret_key=secret_key or settings.FLUTTERWAVE_SECRET_KEY,
            public_key=public_key or settings.FLUTTERWAVE_PUBLIC_KEY,
            webhook_secret=webhook_secret,
            **config,
        )
        self.base_url = config.get("base_url", FLUTTERWAVE_BASE_URL)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    def initialize_payment(self, request: PaymentInitRequest) -> PaymentInitResponse:
        payload = {
            "tx_ref": request.reference,
            "amount": str(request.amount),
            "currency": request.currency,
            "redirect_url": request.callback_url,
            "customer": {"email": request.email},
            "meta": request.metadata,
            "customizations": {"description": request.description or "EstateOS Payment"},
        }
        try:
            response = requests.post(
                f"{self.base_url}/payments",
                json=payload,
                headers=self._headers(),
                timeout=30,
            )
            data = response.json()
            if data.get("status") == "success" and data.get("data"):
                return PaymentInitResponse(
                    success=True,
                    reference=request.reference,
                    authorization_url=data["data"].get("link", ""),
                    provider_reference=str(data["data"].get("id", "")),
                    raw_response=data,
                )
            return PaymentInitResponse(
                success=False,
                reference=request.reference,
                error_message=data.get("message", "Payment initialization failed"),
                raw_response=data,
            )
        except requests.RequestException as exc:
            logger.exception("Flutterwave initialize failed: %s", exc)
            return PaymentInitResponse(
                success=False,
                reference=request.reference,
                error_message=str(exc),
            )

    def verify_payment(self, reference: str) -> PaymentVerifyResponse:
        try:
            response = requests.get(
                f"{self.base_url}/transactions/verify_by_reference",
                params={"tx_ref": reference},
                headers=self._headers(),
                timeout=30,
            )
            data = response.json()
            if data.get("status") == "success" and data.get("data"):
                txn = data["data"]
                return PaymentVerifyResponse(
                    success=txn.get("status") == "successful",
                    status=txn.get("status", "failed"),
                    amount=Decimal(str(txn.get("amount", 0))),
                    currency=txn.get("currency", "NGN"),
                    reference=txn.get("tx_ref", reference),
                    provider_reference=str(txn.get("id", "")),
                    paid_at=txn.get("created_at"),
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
            logger.exception("Flutterwave verify failed: %s", exc)
            return PaymentVerifyResponse(
                success=False,
                status="failed",
                amount=Decimal("0"),
                currency="NGN",
                reference=reference,
                error_message=str(exc),
            )

    def refund_payment(self, request: RefundRequest) -> RefundResponse:
        payload = {"id": request.transaction_reference}
        if request.amount:
            payload["amount"] = str(request.amount)
        try:
            response = requests.post(
                f"{self.base_url}/transactions/{request.transaction_reference}/refund",
                json=payload,
                headers=self._headers(),
                timeout=30,
            )
            data = response.json()
            if data.get("status") == "success":
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
            logger.exception("Flutterwave refund failed: %s", exc)
            return RefundResponse(success=False, error_message=str(exc))

    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        import hmac as _hmac
        secret = self.webhook_secret or self.secret_key
        if not secret or not signature:
            return False
        computed = hashlib.sha256(payload + secret.encode("utf-8")).hexdigest()
        return _hmac.compare_digest(computed, signature)
