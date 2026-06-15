from django.db import models
from django.utils import timezone

from core.models import TenantBaseModel


class RideRequest(TenantBaseModel):
    """On-demand transportation ride request."""

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        MATCHED = "matched", "Driver Matched"
        EN_ROUTE = "en_route", "En Route"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class RideType(models.TextChoices):
        STANDARD = "standard", "Standard"
        PREMIUM = "premium", "Premium"
        SHARED = "shared", "Shared"

    requester = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="ride_requests")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED, db_index=True)
    ride_type = models.CharField(max_length=20, choices=RideType.choices, default=RideType.STANDARD)
    pickup_address = models.TextField()
    dropoff_address = models.TextField()
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    dropoff_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    dropoff_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True, db_index=True)
    driver_name = models.CharField(max_length=255, blank=True)
    driver_phone = models.CharField(max_length=20, blank=True)
    vehicle_description = models.CharField(max_length=255, blank=True)
    estimated_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="NGN")
    payment_reference = models.CharField(max_length=100, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    passenger_count = models.PositiveSmallIntegerField(default=1)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "transportation_ride_request"
        indexes = [
            models.Index(fields=["estate", "status", "created_at"]),
            models.Index(fields=["requester", "status"]),
            models.Index(fields=["scheduled_at"]),
        ]
