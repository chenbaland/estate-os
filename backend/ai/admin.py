from django.contrib import admin

from ai import models

@admin.register(models.Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Embedding)
class EmbeddingAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(models.Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
