from notifications.channels.base import BaseNotificationChannel
from notifications.channels.email import EmailChannel
from notifications.channels.inapp import InAppChannel
from notifications.channels.push import PushChannel
from notifications.channels.sms import SMSChannel
from notifications.channels.whatsapp import WhatsAppChannel

CHANNEL_REGISTRY = {
    "email": EmailChannel,
    "sms": SMSChannel,
    "whatsapp": WhatsAppChannel,
    "push": PushChannel,
    "inapp": InAppChannel,
}


def get_notification_channel(channel_name: str, **kwargs) -> BaseNotificationChannel:
    """Factory function to instantiate a notification channel."""
    channel_class = CHANNEL_REGISTRY.get(channel_name)
    if not channel_class:
        raise ValueError(f"Unknown notification channel: {channel_name}")
    return channel_class(**kwargs)
