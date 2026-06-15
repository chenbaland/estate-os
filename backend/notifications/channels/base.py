"""
Abstract notification channel interface.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class NotificationPayload:
    recipient_id: str
    title: str
    body: str
    channel: str
    data: dict = field(default_factory=dict)
    action_url: str = ""
    template_code: str = ""
    locale: str = "en"


@dataclass
class DeliveryResult:
    success: bool
    external_id: str = ""
    error_message: str = ""
    raw_response: dict = field(default_factory=dict)


class BaseNotificationChannel(ABC):
    """Abstract base class for notification delivery channels."""

    channel_name: str = "base"

    @abstractmethod
    def send(self, payload: NotificationPayload) -> DeliveryResult:
        """Send a notification through this channel."""

    def is_available(self) -> bool:
        """Check if the channel is configured and available."""
        return True

    def validate_recipient(self, recipient_id: str) -> bool:
        """Validate recipient identifier for this channel."""
        return bool(recipient_id)
