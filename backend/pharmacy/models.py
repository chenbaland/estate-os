from django.db import models
from django.utils import timezone

from core.models import TenantBaseModel


class Prescription(TenantBaseModel):
    """Medical prescription uploaded or issued to a resident."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Verification"
        VERIFIED = "verified", "Verified"
        FULFILLED = "fulfilled", "Fulfilled"
        REJECTED = "rejected", "Rejected"
        EXPIRED = "expired", "Expired"

    resident = models.ForeignKey("residents.ResidentProfile", on_delete=models.CASCADE, related_name="prescriptions")
    doctor_name = models.CharField(max_length=255, blank=True)
    hospital_name = models.CharField(max_length=255, blank=True)
    prescription_number = models.CharField(max_length=100, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    image = models.ImageField(upload_to="pharmacy/prescriptions/%Y/%m/")
    medications = models.JSONField(default=list)
    issued_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True, db_index=True)
    verified_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_prescriptions",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "pharmacy_prescription"
        indexes = [
            models.Index(fields=["estate", "resident", "status"]),
            models.Index(fields=["expiry_date", "status"]),
        ]


class MedicationOrder(TenantBaseModel):
    """Order for prescription medication fulfillment."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PREPARING = "preparing", "Preparing"
        READY = "ready", "Ready for Pickup"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="orders")
    resident = models.ForeignKey("residents.ResidentProfile", on_delete=models.CASCADE, related_name="medication_orders")
    order_number = models.CharField(max_length=50, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    items = models.JSONField(default=list)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="NGN")
    delivery_type = models.CharField(max_length=20, default="pickup")
    delivery_address = models.TextField(blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "pharmacy_medication_order"
        unique_together = [("estate", "order_number")]
        indexes = [
            models.Index(fields=["estate", "status", "created_at"]),
            models.Index(fields=["resident", "status"]),
        ]


class DrugReminder(TenantBaseModel):
    """Medication reminder schedule for a resident."""

    class Frequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        CUSTOM = "custom", "Custom"

    resident = models.ForeignKey("residents.ResidentProfile", on_delete=models.CASCADE, related_name="drug_reminders")
    medication_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=Frequency.choices, default=Frequency.DAILY)
    schedule = models.JSONField(default=list)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    last_reminded_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "pharmacy_drug_reminder"
        indexes = [
            models.Index(fields=["estate", "resident", "is_active"]),
        ]
