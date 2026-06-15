from django.contrib import admin

from transportation import models

@admin.register(models.RideRequest)
class RideRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
