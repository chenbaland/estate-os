from django.conf import settings
from django.db import models

from core.models import TimeStampedModel, UUIDModel


class PlatformAuditLog(UUIDModel, TimeStampedModel):
    """Immutable record of super-admin actions on the platform."""

    class Action(models.TextChoices):
        ESTATE_CREATED = "estate.created", "Estate created"
        ESTATE_UPDATED = "estate.updated", "Estate updated"
        ESTATE_DEACTIVATED = "estate.deactivated", "Estate deactivated"
        ESTATE_ACTIVATED = "estate.activated", "Estate activated"
        ADMIN_ASSIGNED = "admin.assigned", "Admin assigned"
        ADMIN_REVOKED = "admin.revoked", "Admin revoked"

    action = models.CharField(max_length=64, choices=Action.choices, db_index=True)
    resource_type = models.CharField(max_length=64, db_index=True)
    resource_id = models.UUIDField(null=True, blank=True, db_index=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="platform_audit_logs",
    )
    estate = models.ForeignKey(
        "estates.Estate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="platform_audit_logs",
    )
    summary = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    trace_id = models.CharField(max_length=64, blank=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at", "action"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} — {self.summary}"
