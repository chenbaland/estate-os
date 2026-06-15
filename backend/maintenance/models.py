from django.db import models
from django.utils import timezone

from core.models import TenantBaseModel


class SLAConfig(TenantBaseModel):
    """Service level agreement configuration for maintenance tickets."""

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    name = models.CharField(max_length=100)
    priority = models.CharField(max_length=20, choices=Priority.choices, unique=False)
    category = models.CharField(max_length=100, blank=True, db_index=True)
    response_time_hours = models.PositiveIntegerField(default=24)
    resolution_time_hours = models.PositiveIntegerField(default=72)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "maintenance_sla_config"
        unique_together = [("estate", "priority", "category")]
        indexes = [
            models.Index(fields=["estate", "is_active"]),
        ]


class Ticket(TenantBaseModel):
    """Maintenance service request ticket."""

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ASSIGNED = "assigned", "Assigned"
        IN_PROGRESS = "in_progress", "In Progress"
        ON_HOLD = "on_hold", "On Hold"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Category(models.TextChoices):
        PLUMBING = "plumbing", "Plumbing"
        ELECTRICAL = "electrical", "Electrical"
        HVAC = "hvac", "HVAC"
        STRUCTURAL = "structural", "Structural"
        APPLIANCE = "appliance", "Appliance"
        PEST = "pest", "Pest Control"
        GENERAL = "general", "General"
        OTHER = "other", "Other"

    ticket_number = models.CharField(max_length=50, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices, db_index=True)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    unit = models.ForeignKey("estates.Unit", on_delete=models.CASCADE, related_name="maintenance_tickets")
    reported_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="reported_tickets")
    assigned_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )
    sla_config = models.ForeignKey(SLAConfig, on_delete=models.SET_NULL, null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "maintenance_ticket"
        unique_together = [("estate", "ticket_number")]
        indexes = [
            models.Index(fields=["estate", "status", "priority"]),
            models.Index(fields=["unit", "status"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["due_at"]),
        ]


class TicketComment(TenantBaseModel):
    """Comment or update on a maintenance ticket."""

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    body = models.TextField()
    is_internal = models.BooleanField(default=False)
    attachments = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "maintenance_ticket_comment"
        indexes = [
            models.Index(fields=["estate", "ticket", "created_at"]),
        ]
