from django.db import models

from core.models import TenantBaseModel


class NotificationTemplate(TenantBaseModel):
    """Reusable notification template."""

    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        WHATSAPP = "whatsapp", "WhatsApp"
        PUSH = "push", "Push"
        INAPP = "inapp", "In-App"

    code = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=255)
    channel = models.CharField(max_length=20, choices=Channel.choices, db_index=True)
    subject = models.CharField(max_length=255, blank=True)
    body_template = models.TextField()
    html_template = models.TextField(blank=True)
    variables = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    locale = models.CharField(max_length=10, default="en")

    class Meta:
        db_table = "notifications_template"
        unique_together = [("estate", "code", "channel", "locale")]
        indexes = [
            models.Index(fields=["estate", "code", "is_active"]),
        ]


class NotificationPreference(TenantBaseModel):
    """User notification channel preferences."""

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="notification_preferences")
    channel = models.CharField(max_length=20, choices=NotificationTemplate.Channel.choices)
    category = models.CharField(max_length=100, default="general", db_index=True)
    is_enabled = models.BooleanField(default=True)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "notifications_preference"
        unique_together = [("estate", "user", "channel", "category")]
        indexes = [
            models.Index(fields=["estate", "user", "is_enabled"]),
        ]


class Notification(TenantBaseModel):
    """Delivered or pending notification."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        READ = "read", "Read"
        FAILED = "failed", "Failed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    recipient = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="notifications")
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    channel = models.CharField(max_length=20, choices=NotificationTemplate.Channel.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.NORMAL)
    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    action_url = models.URLField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    external_id = models.CharField(max_length=255, blank=True, db_index=True)

    class Meta:
        db_table = "notifications_notification"
        indexes = [
            models.Index(fields=["estate", "recipient", "status"]),
            models.Index(fields=["recipient", "channel", "status"]),
            models.Index(fields=["created_at"]),
        ]
