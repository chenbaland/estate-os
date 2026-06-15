from django.contrib import admin

from community import models

@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.LostFound)
class LostFoundAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
