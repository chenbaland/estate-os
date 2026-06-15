"""
Abstract payment provider interface for EstateOS.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Optional


@dataclass
class PaymentInitRequest:
    amount: Decimal
    currency: str
    email: str
    reference: str
    callback_url: str = ""
    metadata: dict = field(default_factory=dict)
    description: str = ""


@dataclass
class PaymentInitResponse:
    success: bool
    reference: str
    authorization_url: str = ""
    access_code: str = ""
    provider_reference: str = ""
    raw_response: dict = field(default_factory=dict)
    error_message: str = ""


@dataclass
class PaymentVerifyResponse:
    success: bool
    status: str
    amount: Decimal
    currency: str
    reference: str
    provider_reference: str = ""
    paid_at: Optional[str] = None
    raw_response: dict = field(default_factory=dict)
    error_message: str = ""


@dataclass
class RefundRequest:
    transaction_reference: str
    amount: Optional[Decimal] = None
    reason: str = ""


@dataclass
class RefundResponse:
    success: bool
    refund_reference: str = ""
    status: str = ""
    raw_response: dict = field(default_factory=dict)
    error_message: str = ""


class BasePaymentProvider(ABC):
    """Abstract base class for payment provider integrations."""

    provider_name: str = "base"

    def __init__(self, secret_key: str, public_key: str = "", webhook_secret: str = "", **config):
        self.secret_key = secret_key
        self.public_key = public_key
        self.webhook_secret = webhook_secret
        self.config = config

    @abstractmethod
    def initialize_payment(self, request: PaymentInitRequest) -> PaymentInitResponse:
        """Initialize a payment transaction."""

    @abstractmethod
    def verify_payment(self, reference: str) -> PaymentVerifyResponse:
        """Verify a payment by reference."""

    @abstractmethod
    def refund_payment(self, request: RefundRequest) -> RefundResponse:
        """Process a refund."""

    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Validate incoming webhook signature."""
        return False

    def parse_webhook_event(self, payload: dict) -> dict[str, Any]:
        """Parse webhook payload into normalized event data."""
        return {"event": payload.get("event", "unknown"), "data": payload}
