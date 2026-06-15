from django.contrib import admin

from security import models

@admin.register(models.Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.PatrolLog)
class PatrolLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.EmergencyBroadcast)
class EmergencyBroadcastAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
