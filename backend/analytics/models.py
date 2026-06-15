from django.db import models

from core.models import TenantBaseModel


class DashboardWidget(TenantBaseModel):
    """Configurable analytics dashboard widget."""

    class WidgetType(models.TextChoices):
        CHART = "chart", "Chart"
        KPI = "kpi", "KPI Card"
        TABLE = "table", "Table"
        MAP = "map", "Map"
        LIST = "list", "List"

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WidgetType.choices)
    description = models.TextField(blank=True)
    query_config = models.JSONField(default=dict)
    display_config = models.JSONField(default=dict)
    refresh_interval_seconds = models.PositiveIntegerField(default=300)
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    allowed_roles = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "analytics_dashboard_widget"
        unique_together = [("estate", "slug")]
        indexes = [
            models.Index(fields=["estate", "is_active", "sort_order"]),
        ]


class MetricSnapshot(TenantBaseModel):
    """Point-in-time metric snapshot for analytics."""

    metric_key = models.CharField(max_length=100, db_index=True)
    metric_name = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=20, decimal_places=4)
    unit = models.CharField(max_length=50, blank=True)
    dimensions = models.JSONField(default=dict, blank=True)
    recorded_at = models.DateTimeField(db_index=True)
    period_start = models.DateTimeField(null=True, blank=True)
    period_end = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "analytics_metric_snapshot"
        indexes = [
            models.Index(fields=["estate", "metric_key", "recorded_at"]),
            models.Index(fields=["recorded_at"]),
        ]
