"""
EstateOS URL configuration.
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from platform_admin.views import PlatformOverviewView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", include("core.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/platform/overview/", PlatformOverviewView.as_view(), name="platform-overview"),
    path("api/v1/platform/", include("platform_admin.urls")),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/estates/", include("estates.urls")),
    path("api/v1/residents/", include("residents.urls")),
    path("api/v1/visitors/", include("visitors.urls")),
    path("api/v1/security/", include("security.urls")),
    path("api/v1/billing/", include("billing.urls")),
    path("api/v1/utilities/", include("utilities.urls")),
    path("api/v1/marketplace/", include("marketplace.urls")),
    path("api/v1/pharmacy/", include("pharmacy.urls")),
    path("api/v1/healthcare/", include("healthcare.urls")),
    path("api/v1/facilities/", include("facilities.urls")),
    path("api/v1/maintenance/", include("maintenance.urls")),
    path("api/v1/packages/", include("packages.urls")),
    path("api/v1/parking/", include("parking.urls")),
    path("api/v1/community/", include("community.urls")),
    path("api/v1/transportation/", include("transportation.urls")),
    path("api/v1/analytics/", include("analytics.urls")),
    path("api/v1/ai/", include("ai.urls")),
    path("api/v1/notifications/", include("notifications.urls")),
    path("api/v1/payments/", include("payments.urls")),
]
