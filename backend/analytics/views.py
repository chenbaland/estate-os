from core.viewsets import TenantReadOnlyViewSet, TenantViewSet
from analytics.models import DashboardWidget, MetricSnapshot
from analytics.serializers import DashboardWidgetSerializer, MetricSnapshotSerializer


class DashboardWidgetViewSet(TenantViewSet):
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer
    filterset_fields = ["widget_type", "is_active"]
    search_fields = ["name", "slug", "description"]


class MetricSnapshotViewSet(TenantReadOnlyViewSet):
    queryset = MetricSnapshot.objects.all()
    serializer_class = MetricSnapshotSerializer
    filterset_fields = ["metric_key"]
    search_fields = ["metric_key", "metric_name"]
    ordering_fields = ["recorded_at", "created_at", "metric_key"]
    ordering = ["-recorded_at"]
