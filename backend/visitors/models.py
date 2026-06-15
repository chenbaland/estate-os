from django.db import models
from django.utils import timezone

from core.models import TenantBaseModel


class VisitorPass(TenantBaseModel):
    """Pre-authorized visitor pass with QR code."""

    class PassType(models.TextChoices):
        SINGLE = "single", "Single Entry"
        MULTI = "multi", "Multi Entry"
        RECURRING = "recurring", "Recurring"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        USED = "used", "Used"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    host = models.ForeignKey("residents.ResidentProfile", on_delete=models.CASCADE, related_name="visitor_passes")
    visitor_name = models.CharField(max_length=255)
    visitor_phone = models.CharField(max_length=20, blank=True)
    visitor_email = models.EmailField(blank=True)
    visitor_company = models.CharField(max_length=255, blank=True)
    pass_type = models.CharField(max_length=20, choices=PassType.choices, default=PassType.SINGLE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    qr_code = models.CharField(max_length=255, unique=True, db_index=True)
    access_code = models.CharField(max_length=10, blank=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(db_index=True)
    max_entries = models.PositiveSmallIntegerField(default=1)
    entries_used = models.PositiveSmallIntegerField(default=0)
    vehicle_plate = models.CharField(max_length=20, blank=True)
    purpose = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to="visitors/photos/%Y/%m/", blank=True, null=True)

    class Meta:
        db_table = "visitors_pass"
        indexes = [
            models.Index(fields=["estate", "status", "valid_until"]),
            models.Index(fields=["host", "status"]),
            models.Index(fields=["qr_code"]),
        ]


class VisitorLog(TenantBaseModel):
    """Gate entry/exit log for visitors."""

    class Direction(models.TextChoices):
        ENTRY = "entry", "Entry"
        EXIT = "exit", "Exit"

    class VerificationMethod(models.TextChoices):
        QR = "qr", "QR Code"
        MANUAL = "manual", "Manual"
        RFID = "rfid", "RFID"
        OTP = "otp", "OTP"

    visitor_pass = models.ForeignKey(
        VisitorPass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
    )
    visitor_name = models.CharField(max_length=255)
    visitor_phone = models.CharField(max_length=20, blank=True)
    host = models.ForeignKey(
        "residents.ResidentProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visitor_logs",
    )
    direction = models.CharField(max_length=10, choices=Direction.choices)
    verification_method = models.CharField(max_length=20, choices=VerificationMethod.choices)
    gate_name = models.CharField(max_length=100, blank=True)
    vehicle_plate = models.CharField(max_length=20, blank=True)
    verified_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_visitors",
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    photo = models.ImageField(upload_to="visitors/logs/%Y/%m/", blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "visitors_log"
        indexes = [
            models.Index(fields=["estate", "timestamp"]),
            models.Index(fields=["estate", "direction", "timestamp"]),
            models.Index(fields=["visitor_pass"]),
        ]


class Blacklist(TenantBaseModel):
    """Blacklisted individuals denied estate access."""

    class Reason(models.TextChoices):
        SECURITY = "security", "Security Incident"
        TRESPASS = "trespass", "Trespassing"
        FRAUD = "fraud", "Fraud"
        DISTURBANCE = "disturbance", "Disturbance"
        OTHER = "other", "Other"

    full_name = models.CharField(max_length=255, db_index=True)
    phone = models.CharField(max_length=20, blank=True, db_index=True)
    email = models.EmailField(blank=True)
    id_document_number = models.CharField(max_length=100, blank=True, db_index=True)
    license_plate = models.CharField(max_length=20, blank=True, db_index=True)
    photo = models.ImageField(upload_to="visitors/blacklist/%Y/%m/", blank=True, null=True)
    reason = models.CharField(max_length=20, choices=Reason.choices)
    description = models.TextField()
    reported_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="blacklist_reports",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "visitors_blacklist"
        indexes = [
            models.Index(fields=["estate", "is_active"]),
            models.Index(fields=["full_name", "phone"]),
        ]
