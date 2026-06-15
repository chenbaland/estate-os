"""
Push notification channel (FCM).
"""
import logging

import requests
from django.conf import settings

from notifications.channels.base import BaseNotificationChannel, DeliveryResult, NotificationPayload

logger = logging.getLogger("estateos.notifications.push")


class PushChannel(BaseNotificationChannel):
    channel_name = "push"

    def __init__(self, server_key: str = ""):
        self.server_key = server_key or settings.FCM_SERVER_KEY

    def is_available(self) -> bool:
        return bool(self.server_key)

    def send(self, payload: NotificationPayload) -> DeliveryResult:
        if not self.is_available():
            return DeliveryResult(success=False, error_message="FCM not configured")

        try:
            response = requests.post(
                "https://fcm.googleapis.com/fcm/send",
                headers={
                    "Authorization": f"key={self.server_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "to": payload.recipient_id,
                    "notification": {
                        "title": payload.title,
                        "body": payload.body,
                    },
                    "data": payload.data,
                },
                timeout=30,
            )
            data = response.json()
            if data.get("success", 0) > 0:
                return DeliveryResult(
                    success=True,
                    external_id=str(data.get("multicast_id", "")),
                    raw_response=data,
                )
            return DeliveryResult(
                success=False,
                error_message=str(data.get("results", [{}])[0].get("error", "Push send failed")),
                raw_response=data,
            )
        except Exception as exc:
            logger.exception("Push delivery failed: %s", exc)
            return DeliveryResult(success=False, error_message=str(exc))
