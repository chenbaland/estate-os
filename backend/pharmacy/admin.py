from django.contrib import admin

from pharmacy import models

@admin.register(models.Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.MedicationOrder)
class MedicationOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.DrugReminder)
class DrugReminderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
