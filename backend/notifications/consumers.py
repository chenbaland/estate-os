import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger("estateos.notifications.websocket")


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time in-app notifications."""

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close()
            return

        self.group_name = f"user_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info("WebSocket connected for user %s", user.id)

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                data = json.loads(text_data)
                if data.get("type") == "ping":
                    await self.send(text_data=json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                pass

    async def notification_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "notification",
                    "title": event.get("title", ""),
                    "body": event.get("body", ""),
                    "data": event.get("data", {}),
                    "action_url": event.get("action_url", ""),
                }
            )
        )
