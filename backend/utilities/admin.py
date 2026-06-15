from django.contrib import admin

from utilities import models

@admin.register(models.UtilityAccount)
class UtilityAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.UtilityTransaction)
class UtilityTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.ConsumptionRecord)
class ConsumptionRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
