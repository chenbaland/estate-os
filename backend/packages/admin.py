from django.contrib import admin

from packages import models

@admin.register(models.Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.PackageLog)
class PackageLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
