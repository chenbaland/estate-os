from rest_framework.routers import DefaultRouter

from notifications.views import NotificationPreferenceViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"preferences", NotificationPreferenceViewSet, basename="notification-preference")

urlpatterns = router.urls
