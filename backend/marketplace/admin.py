from django.contrib import admin

from marketplace import models

@admin.register(models.Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
