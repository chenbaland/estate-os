"""
WhatsApp notification channel.
"""
import logging

import requests
from django.conf import settings

from notifications.channels.base import BaseNotificationChannel, DeliveryResult, NotificationPayload

logger = logging.getLogger("estateos.notifications.whatsapp")


class WhatsAppChannel(BaseNotificationChannel):
    channel_name = "whatsapp"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or settings.WHATSAPP_API_KEY

    def is_available(self) -> bool:
        return bool(self.api_key)

    def send(self, payload: NotificationPayload) -> DeliveryResult:
        if not self.is_available():
            return DeliveryResult(success=False, error_message="WhatsApp provider not configured")

        try:
            response = requests.post(
                "https://graph.facebook.com/v18.0/me/messages",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "messaging_product": "whatsapp",
                    "to": payload.recipient_id,
                    "type": "text",
                    "text": {"body": f"*{payload.title}*\n{payload.body}" if payload.title else payload.body},
                },
                timeout=30,
            )
            data = response.json()
            message_id = data.get("messages", [{}])[0].get("id", "")
            if message_id:
                return DeliveryResult(success=True, external_id=message_id, raw_response=data)
            return DeliveryResult(
                success=False,
                error_message=data.get("error", {}).get("message", "WhatsApp send failed"),
                raw_response=data,
            )
        except Exception as exc:
            logger.exception("WhatsApp delivery failed: %s", exc)
            return DeliveryResult(success=False, error_message=str(exc))
