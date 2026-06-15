from django.db import models

from core.models import TenantBaseModel


class Conversation(TenantBaseModel):
    """AI assistant conversation session."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"
        ESCALATED = "escalated", "Escalated to Human"

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="ai_conversations")
    title = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    context = models.JSONField(default=dict, blank=True)
    message_count = models.PositiveIntegerField(default=0)
    last_message_at = models.DateTimeField(null=True, blank=True)
    model_name = models.CharField(max_length=100, default="gpt-4")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "ai_conversation"
        indexes = [
            models.Index(fields=["estate", "user", "status"]),
            models.Index(fields=["last_message_at"]),
        ]


class Document(TenantBaseModel):
    """Document indexed for AI retrieval."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Processing"
        PROCESSING = "processing", "Processing"
        INDEXED = "indexed", "Indexed"
        FAILED = "failed", "Failed"

    class DocumentType(models.TextChoices):
        POLICY = "policy", "Policy Document"
        FAQ = "faq", "FAQ"
        MANUAL = "manual", "Manual"
        ANNOUNCEMENT = "announcement", "Announcement"
        OTHER = "other", "Other"

    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DocumentType.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    file = models.FileField(upload_to="ai/documents/%Y/%m/", blank=True, null=True)
    content_text = models.TextField(blank=True)
    source_url = models.URLField(blank=True)
    chunk_count = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "ai_document"
        indexes = [
            models.Index(fields=["estate", "document_type", "status"]),
        ]


class Embedding(TenantBaseModel):
    """Vector embedding for a document chunk."""

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="embeddings")
    chunk_index = models.PositiveIntegerField()
    chunk_text = models.TextField()
    embedding_vector = models.JSONField(default=list)
    model_name = models.CharField(max_length=100, default="text-embedding-3-small")
    token_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "ai_embedding"
        unique_together = [("document", "chunk_index")]
        indexes = [
            models.Index(fields=["estate", "document"]),
        ]


class Prediction(TenantBaseModel):
    """AI-generated prediction or insight."""

    class PredictionType(models.TextChoices):
        CHURN = "churn", "Resident Churn"
        PAYMENT = "payment", "Payment Default"
        MAINTENANCE = "maintenance", "Maintenance Forecast"
        SECURITY = "security", "Security Risk"
        USAGE = "usage", "Usage Pattern"
        CUSTOM = "custom", "Custom"

    prediction_type = models.CharField(max_length=20, choices=PredictionType.choices, db_index=True)
    target_entity_type = models.CharField(max_length=100)
    target_entity_id = models.UUIDField(db_index=True)
    score = models.DecimalField(max_digits=5, decimal_places=4)
    confidence = models.DecimalField(max_digits=5, decimal_places=4)
    prediction_data = models.JSONField(default=dict)
    model_name = models.CharField(max_length=100)
    model_version = models.CharField(max_length=50, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "ai_prediction"
        indexes = [
            models.Index(fields=["estate", "prediction_type", "is_active"]),
            models.Index(fields=["target_entity_type", "target_entity_id"]),
        ]
