from rest_framework.routers import DefaultRouter

from analytics.views import DashboardWidgetViewSet, MetricSnapshotViewSet

router = DefaultRouter()
router.register(r"widgets", DashboardWidgetViewSet, basename="dashboard-widget")
router.register(r"metrics", MetricSnapshotViewSet, basename="metric-snapshot")

urlpatterns = router.urls
