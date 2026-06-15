from django.contrib import admin

from analytics import models

@admin.register(models.DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.MetricSnapshot)
class MetricSnapshotAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
