from rest_framework.routers import DefaultRouter

from platform_admin.views import (
    PlatformAdminViewSet,
    PlatformAuditLogViewSet,
    PlatformEstateViewSet,
    PlatformOverviewView,
)

router = DefaultRouter()
router.register(r"estates", PlatformEstateViewSet, basename="platform-estate")
router.register(r"admins", PlatformAdminViewSet, basename="platform-admin")
router.register(r"audit-logs", PlatformAuditLogViewSet, basename="platform-audit-log")

urlpatterns = [
    *router.urls,
]

# Overview is registered separately in config/urls for a clean path
