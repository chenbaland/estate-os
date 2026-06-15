from django.db import models
from django.utils import timezone

from core.models import TenantBaseModel


class Incident(TenantBaseModel):
    """Security incident report."""

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATING = "investigating", "Investigating"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    class Category(models.TextChoices):
        THEFT = "theft", "Theft"
        VANDALISM = "vandalism", "Vandalism"
        TRESPASS = "trespass", "Trespass"
        NOISE = "noise", "Noise Complaint"
        ASSAULT = "assault", "Assault"
        FIRE = "fire", "Fire"
        MEDICAL = "medical", "Medical Emergency"
        OTHER = "other", "Other"

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices, db_index=True)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    location = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    reported_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="reported_incidents",
    )
    assigned_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_incidents",
    )
    occurred_at = models.DateTimeField(default=timezone.now, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    attachments = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "security_incident"
        indexes = [
            models.Index(fields=["estate", "status", "severity"]),
            models.Index(fields=["estate", "occurred_at"]),
            models.Index(fields=["category", "status"]),
        ]


class PatrolLog(TenantBaseModel):
    """Security patrol checkpoint log."""

    class Status(models.TextChoices):
        COMPLETED = "completed", "Completed"
        PARTIAL = "partial", "Partial"
        MISSED = "missed", "Missed"

    officer = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="patrol_logs")
    route_name = models.CharField(max_length=100)
    checkpoint = models.CharField(max_length=100, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.COMPLETED)
    checked_at = models.DateTimeField(default=timezone.now, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to="security/patrols/%Y/%m/", blank=True, null=True)

    class Meta:
        db_table = "security_patrol_log"
        indexes = [
            models.Index(fields=["estate", "checked_at"]),
            models.Index(fields=["officer", "checked_at"]),
        ]


class SOSAlert(TenantBaseModel):
    """Emergency SOS alert from a resident."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESPONDING = "responding", "Responding"
        RESOLVED = "resolved", "Resolved"
        FALSE_ALARM = "false_alarm", "False Alarm"

    resident = models.ForeignKey(
        "residents.ResidentProfile",
        on_delete=models.CASCADE,
        related_name="sos_alerts",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    message = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_description = models.CharField(max_length=255, blank=True)
    acknowledged_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acknowledged_sos",
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    response_notes = models.TextField(blank=True)

    class Meta:
        db_table = "security_sos_alert"
        indexes = [
            models.Index(fields=["estate", "status", "created_at"]),
            models.Index(fields=["resident", "status"]),
        ]


class EmergencyBroadcast(TenantBaseModel):
    """Estate-wide emergency broadcast notification."""

    class Priority(models.TextChoices):
        INFO = "info", "Information"
        WARNING = "warning", "Warning"
        URGENT = "urgent", "Urgent"
        CRITICAL = "critical", "Critical"

    class Channel(models.TextChoices):
        PUSH = "push", "Push Notification"
        SMS = "sms", "SMS"
        EMAIL = "email", "Email"
        ALL = "all", "All Channels"

    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.URGENT)
    channel = models.CharField(max_length=20, choices=Channel.choices, default=Channel.ALL)
    sent_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    sent_at = models.DateTimeField(default=timezone.now, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    recipient_count = models.PositiveIntegerField(default=0)
    delivery_stats = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "security_emergency_broadcast"
        indexes = [
            models.Index(fields=["estate", "is_active", "sent_at"]),
            models.Index(fields=["priority", "sent_at"]),
        ]
