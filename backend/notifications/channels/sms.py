"""
SMS notification channel.
"""
import logging

import requests
from django.conf import settings

from notifications.channels.base import BaseNotificationChannel, DeliveryResult, NotificationPayload

logger = logging.getLogger("estateos.notifications.sms")


class SMSChannel(BaseNotificationChannel):
    channel_name = "sms"

    def __init__(self, api_key: str = "", provider: str = ""):
        self.api_key = api_key or settings.SMS_API_KEY
        self.provider = provider or settings.SMS_PROVIDER

    def is_available(self) -> bool:
        return bool(self.api_key)

    def send(self, payload: NotificationPayload) -> DeliveryResult:
        if not self.is_available():
            return DeliveryResult(success=False, error_message="SMS provider not configured")

        phone = payload.recipient_id
        message = f"{payload.title}\n{payload.body}" if payload.title else payload.body

        try:
            if self.provider == "termii":
                return self._send_termii(phone, message)
            return DeliveryResult(success=False, error_message=f"Unknown SMS provider: {self.provider}")
        except Exception as exc:
            logger.exception("SMS delivery failed: %s", exc)
            return DeliveryResult(success=False, error_message=str(exc))

    def _send_termii(self, phone: str, message: str) -> DeliveryResult:
        response = requests.post(
            "https://api.ng.termii.com/api/sms/send",
            json={
                "to": phone,
                "from": "EstateOS",
                "sms": message,
                "type": "plain",
                "channel": "generic",
                "api_key": self.api_key,
            },
            timeout=30,
        )
        data = response.json()
        if data.get("message_id") or data.get("code") == "ok":
            return DeliveryResult(success=True, external_id=str(data.get("message_id", "")), raw_response=data)
        return DeliveryResult(success=False, error_message=data.get("message", "SMS send failed"), raw_response=data)

    def validate_recipient(self, recipient_id: str) -> bool:
        cleaned = recipient_id.replace("+", "").replace(" ", "")
        return cleaned.isdigit() and len(cleaned) >= 10
