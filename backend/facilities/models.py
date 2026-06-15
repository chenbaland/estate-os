from django.db import models
from django.utils import timezone

from core.models import TenantBaseModel


class Facility(TenantBaseModel):
    """Estate facility available for booking (gym, pool, hall, etc.)."""

    class FacilityType(models.TextChoices):
        GYM = "gym", "Gym"
        POOL = "pool", "Swimming Pool"
        HALL = "hall", "Event Hall"
        TENNIS = "tennis", "Tennis Court"
        BBQ = "bbq", "BBQ Area"
        PLAYGROUND = "playground", "Playground"
        COWORKING = "coworking", "Co-working Space"
        OTHER = "other", "Other"

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100)
    facility_type = models.CharField(max_length=20, choices=FacilityType.choices, db_index=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    capacity = models.PositiveIntegerField(default=1)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="NGN")
    operating_hours = models.JSONField(default=dict, blank=True)
    booking_rules = models.JSONField(default=dict, blank=True)
    images = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    requires_approval = models.BooleanField(default=False)

    class Meta:
        db_table = "facilities_facility"
        unique_together = [("estate", "slug")]
        indexes = [
            models.Index(fields=["estate", "facility_type", "is_active"]),
        ]


class Booking(TenantBaseModel):
    """Facility booking reservation."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"
        NO_SHOW = "no_show", "No Show"

    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="facility_bookings")
    resident = models.ForeignKey(
        "residents.ResidentProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="facility_bookings",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    guest_count = models.PositiveSmallIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_bookings",
    )

    class Meta:
        db_table = "facilities_booking"
        indexes = [
            models.Index(fields=["estate", "facility", "start_time"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["start_time", "end_time"]),
        ]


class BlackoutDate(TenantBaseModel):
    """Dates when a facility is unavailable."""

    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="blackout_dates")
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    reason = models.CharField(max_length=255)
    is_recurring_yearly = models.BooleanField(default=False)

    class Meta:
        db_table = "facilities_blackout_date"
        indexes = [
            models.Index(fields=["estate", "facility", "start_date"]),
        ]
