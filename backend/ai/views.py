from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from ai.models import Conversation, Document, Prediction
from ai.serializers import ConversationChatSerializer, ConversationSerializer, DocumentSerializer, PredictionSerializer
from core.viewsets import TenantReadOnlyViewSet, TenantViewSet


class ConversationViewSet(TenantViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filterset_fields = ["user", "status", "model_name"]
    search_fields = ["title"]

    @action(detail=True, methods=["post"])
    def chat(self, request, pk=None):
        conversation = self.get_object()
        chat_serializer = ConversationChatSerializer(data=request.data)
        chat_serializer.is_valid(raise_exception=True)
        message = chat_serializer.validated_data["message"]

        context = conversation.context or {}
        messages = context.get("messages", [])
        messages.append({"role": "user", "content": message, "timestamp": timezone.now().isoformat()})
        reply = f"I received your message: {message}"
        messages.append({"role": "assistant", "content": reply, "timestamp": timezone.now().isoformat()})
        context["messages"] = messages
        conversation.context = context
        conversation.message_count += 1
        conversation.last_message_at = timezone.now()
        if not conversation.title:
            conversation.title = message[:255]
        conversation.save(update_fields=["context", "message_count", "last_message_at", "title", "updated_at"])

        return Response(
            {
                "conversation_id": str(conversation.id),
                "reply": reply,
                "message_count": conversation.message_count,
            }
        )


class DocumentViewSet(TenantViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filterset_fields = ["document_type", "status", "uploaded_by"]
    search_fields = ["title", "content_text"]


class PredictionViewSet(TenantReadOnlyViewSet):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    filterset_fields = ["prediction_type", "target_entity_type", "is_active"]
    search_fields = ["target_entity_type", "model_name"]
