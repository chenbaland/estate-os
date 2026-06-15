from django.contrib import admin

from healthcare import models

@admin.register(models.Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.AmbulanceRequest)
class AmbulanceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
