from django.contrib import admin

from residents import models

@admin.register(models.ResidentProfile)
class ResidentProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.DomesticStaff)
class DomesticStaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
