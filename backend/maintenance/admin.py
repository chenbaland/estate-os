from django.contrib import admin

from maintenance import models

@admin.register(models.SLAConfig)
class SLAConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
