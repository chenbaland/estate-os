"""
In-app notification channel with WebSocket broadcast support.
"""
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from notifications.channels.base import BaseNotificationChannel, DeliveryResult, NotificationPayload

logger = logging.getLogger("estateos.notifications.inapp")


class InAppChannel(BaseNotificationChannel):
    channel_name = "inapp"

    def send(self, payload: NotificationPayload) -> DeliveryResult:
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"user_{payload.recipient_id}",
                    {
                        "type": "notification.message",
                        "title": payload.title,
                        "body": payload.body,
                        "data": payload.data,
                        "action_url": payload.action_url,
                    },
                )
            return DeliveryResult(success=True, external_id=f"inapp_{payload.recipient_id}")
        except Exception as exc:
            logger.exception("In-app delivery failed: %s", exc)
            return DeliveryResult(success=False, error_message=str(exc))
