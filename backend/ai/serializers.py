from rest_framework import serializers

from ai.models import Conversation, Document, Prediction
from core.serializers import TenantModelSerializer


class ConversationSerializer(TenantModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            "id",
            "estate",
            "user",
            "title",
            "status",
            "context",
            "message_count",
            "last_message_at",
            "model_name",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "message_count", "last_message_at", "created_at", "updated_at"]


class DocumentSerializer(TenantModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "estate",
            "title",
            "document_type",
            "status",
            "file",
            "content_text",
            "source_url",
            "chunk_count",
            "uploaded_by",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "chunk_count", "created_at", "updated_at"]


class PredictionSerializer(TenantModelSerializer):
    class Meta:
        model = Prediction
        fields = [
            "id",
            "estate",
            "prediction_type",
            "target_entity_type",
            "target_entity_id",
            "score",
            "confidence",
            "prediction_data",
            "model_name",
            "model_version",
            "valid_until",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class ConversationChatSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
