from core.serializers import TenantModelSerializer
from analytics.models import DashboardWidget, MetricSnapshot


class DashboardWidgetSerializer(TenantModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = [
            "id",
            "estate",
            "name",
            "slug",
            "widget_type",
            "description",
            "query_config",
            "display_config",
            "refresh_interval_seconds",
            "is_active",
            "sort_order",
            "allowed_roles",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class MetricSnapshotSerializer(TenantModelSerializer):
    class Meta:
        model = MetricSnapshot
        fields = [
            "id",
            "estate",
            "metric_key",
            "metric_name",
            "value",
            "unit",
            "dimensions",
            "recorded_at",
            "period_start",
            "period_end",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
