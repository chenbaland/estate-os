from django.contrib import admin

from facilities import models

@admin.register(models.Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.BlackoutDate)
class BlackoutDateAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
