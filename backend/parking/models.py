from django.db import models
from django.utils import timezone

from core.models import TenantBaseModel


class ParkingSlot(TenantBaseModel):
    """Designated parking slot within an estate."""

    class SlotType(models.TextChoices):
        RESIDENT = "resident", "Resident"
        VISITOR = "visitor", "Visitor"
        EV = "ev", "EV Charging"
        DISABLED = "disabled", "Disabled Access"
        COMMERCIAL = "commercial", "Commercial"

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        OCCUPIED = "occupied", "Occupied"
        RESERVED = "reserved", "Reserved"
        MAINTENANCE = "maintenance", "Under Maintenance"

    slot_number = models.CharField(max_length=50, db_index=True)
    slot_type = models.CharField(max_length=20, choices=SlotType.choices, default=SlotType.RESIDENT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE, db_index=True)
    location = models.CharField(max_length=255, blank=True)
    block = models.ForeignKey("estates.Block", on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.ForeignKey("estates.Unit", on_delete=models.SET_NULL, null=True, blank=True, related_name="parking_slots")
    has_ev_charger = models.BooleanField(default=False)
    is_covered = models.BooleanField(default=False)
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "parking_slot"
        unique_together = [("estate", "slot_number")]
        indexes = [
            models.Index(fields=["estate", "slot_type", "status"]),
            models.Index(fields=["unit"]),
        ]


class ParkingPermit(TenantBaseModel):
    """Parking permit assigned to a resident vehicle."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"
        SUSPENDED = "suspended", "Suspended"

    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name="permits")
    vehicle = models.ForeignKey("residents.Vehicle", on_delete=models.CASCADE, related_name="parking_permits")
    resident = models.ForeignKey("residents.ResidentProfile", on_delete=models.CASCADE, related_name="parking_permits")
    permit_number = models.CharField(max_length=50, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    valid_from = models.DateField(default=timezone.now)
    valid_until = models.DateField(db_index=True)
    qr_code = models.CharField(max_length=255, blank=True, unique=True, null=True)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = "parking_permit"
        unique_together = [("estate", "permit_number")]
        indexes = [
            models.Index(fields=["estate", "status", "valid_until"]),
            models.Index(fields=["vehicle", "status"]),
        ]


class EVChargingSession(TenantBaseModel):
    """Electric vehicle charging session."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name="ev_sessions")
    vehicle = models.ForeignKey("residents.Vehicle", on_delete=models.CASCADE, related_name="ev_sessions")
    resident = models.ForeignKey("residents.ResidentProfile", on_delete=models.CASCADE, related_name="ev_sessions")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    energy_kwh = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="NGN")
    charger_id = models.CharField(max_length=100, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "parking_ev_charging_session"
        indexes = [
            models.Index(fields=["estate", "status", "started_at"]),
            models.Index(fields=["vehicle", "status"]),
        ]
