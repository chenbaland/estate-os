from django.contrib import admin

from visitors import models

@admin.register(models.VisitorPass)
class VisitorPassAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Blacklist)
class BlacklistAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
