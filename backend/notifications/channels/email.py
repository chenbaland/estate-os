"""
Email notification channel.
"""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from notifications.channels.base import BaseNotificationChannel, DeliveryResult, NotificationPayload

logger = logging.getLogger("estateos.notifications.email")


class EmailChannel(BaseNotificationChannel):
    channel_name = "email"

    def send(self, payload: NotificationPayload) -> DeliveryResult:
        try:
            email = payload.recipient_id
            if not self.validate_recipient(email):
                return DeliveryResult(success=False, error_message="Invalid email address")

            msg = EmailMultiAlternatives(
                subject=payload.title,
                body=payload.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            html_body = payload.data.get("html_body")
            if html_body:
                msg.attach_alternative(html_body, "text/html")
            msg.send(fail_silently=False)

            return DeliveryResult(success=True, external_id=msg.extra_headers.get("Message-ID", ""))
        except Exception as exc:
            logger.exception("Email delivery failed: %s", exc)
            return DeliveryResult(success=False, error_message=str(exc))

    def validate_recipient(self, recipient_id: str) -> bool:
        return "@" in recipient_id and "." in recipient_id.split("@")[-1]
