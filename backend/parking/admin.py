from django.contrib import admin

from parking import models

@admin.register(models.ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.ParkingPermit)
class ParkingPermitAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.EVChargingSession)
class EVChargingSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
