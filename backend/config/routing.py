from django.urls import path

from notifications import consumers as notification_consumers

websocket_urlpatterns = [
    path("ws/notifications/", notification_consumers.NotificationConsumer.as_asgi()),
]
