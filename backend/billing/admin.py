from django.contrib import admin

from billing import models

@admin.register(models.FeeType)
class FeeTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.InvoiceLine)
class InvoiceLineAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.DebtRecord)
class DebtRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
