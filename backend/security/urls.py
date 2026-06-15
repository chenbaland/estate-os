from rest_framework.routers import DefaultRouter

from security.views import (
    EmergencyBroadcastViewSet,
    IncidentViewSet,
    PatrolLogViewSet,
    SOSAlertViewSet,
)

router = DefaultRouter()
router.register(r"incidents", IncidentViewSet, basename="incident")
router.register(r"patrol-logs", PatrolLogViewSet, basename="patrol-log")
router.register(r"sos-alerts", SOSAlertViewSet, basename="sos-alert")
router.register(r"emergency-broadcasts", EmergencyBroadcastViewSet, basename="emergency-broadcast")

urlpatterns = router.urls
