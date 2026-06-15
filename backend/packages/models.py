from django.db import models
from django.utils import timezone

from core.models import TenantBaseModel


class Package(TenantBaseModel):
    """Incoming or outgoing package for a resident."""

    class Status(models.TextChoices):
        EXPECTED = "expected", "Expected"
        RECEIVED = "received", "Received at Gate"
        NOTIFIED = "notified", "Resident Notified"
        COLLECTED = "collected", "Collected"
        RETURNED = "returned", "Returned to Sender"
        LOST = "lost", "Lost"

    class PackageType(models.TextChoices):
        INCOMING = "incoming", "Incoming"
        OUTGOING = "outgoing", "Outgoing"

    tracking_number = models.CharField(max_length=100, db_index=True)
    recipient = models.ForeignKey("residents.ResidentProfile", on_delete=models.CASCADE, related_name="packages")
    unit = models.ForeignKey("estates.Unit", on_delete=models.CASCADE, related_name="packages")
    package_type = models.CharField(max_length=20, choices=PackageType.choices, default=PackageType.INCOMING)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EXPECTED, db_index=True)
    carrier = models.CharField(max_length=100, blank=True)
    sender_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    size = models.CharField(max_length=50, blank=True)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    collected_at = models.DateTimeField(null=True, blank=True)
    storage_location = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to="packages/%Y/%m/", blank=True, null=True)
    otp_code = models.CharField(max_length=10, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "packages_package"
        indexes = [
            models.Index(fields=["estate", "status", "created_at"]),
            models.Index(fields=["recipient", "status"]),
            models.Index(fields=["tracking_number"]),
        ]


class PackageLog(TenantBaseModel):
    """Audit log for package status changes."""

    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="logs")
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    notes = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "packages_log"
        indexes = [
            models.Index(fields=["estate", "package", "timestamp"]),
        ]
