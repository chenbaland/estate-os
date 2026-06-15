from django.db import models
from django.utils import timezone

from core.models import TenantBaseModel


class Hospital(TenantBaseModel):
    """Partner hospital or clinic."""

    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    specialties = models.JSONField(default=list, blank=True)
    operating_hours = models.JSONField(default=dict, blank=True)
    is_partner = models.BooleanField(default=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    class Meta:
        db_table = "healthcare_hospital"
        unique_together = [("estate", "slug")]
        indexes = [
            models.Index(fields=["estate", "is_active", "is_partner"]),
        ]


class Appointment(TenantBaseModel):
    """Medical appointment booking."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    resident = models.ForeignKey("residents.ResidentProfile", on_delete=models.CASCADE, related_name="appointments")
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="appointments")
    doctor_name = models.CharField(max_length=255, blank=True)
    specialty = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    scheduled_at = models.DateTimeField(db_index=True)
    duration_minutes = models.PositiveSmallIntegerField(default=30)
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    reminder_sent = models.BooleanField(default=False)

    class Meta:
        db_table = "healthcare_appointment"
        indexes = [
            models.Index(fields=["estate", "resident", "status"]),
            models.Index(fields=["hospital", "scheduled_at"]),
            models.Index(fields=["scheduled_at", "status"]),
        ]


class AmbulanceRequest(TenantBaseModel):
    """Emergency ambulance dispatch request."""

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        DISPATCHED = "dispatched", "Dispatched"
        EN_ROUTE = "en_route", "En Route"
        ARRIVED = "arrived", "Arrived"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        ROUTINE = "routine", "Routine"
        URGENT = "urgent", "Urgent"
        EMERGENCY = "emergency", "Emergency"

    resident = models.ForeignKey("residents.ResidentProfile", on_delete=models.CASCADE, related_name="ambulance_requests")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED, db_index=True)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.EMERGENCY)
    pickup_location = models.TextField()
    destination_hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ambulance_destinations",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    patient_condition = models.TextField(blank=True)
    dispatched_at = models.DateTimeField(null=True, blank=True)
    arrived_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "healthcare_ambulance_request"
        indexes = [
            models.Index(fields=["estate", "status", "priority"]),
            models.Index(fields=["resident", "status"]),
        ]


class MedicalRecord(TenantBaseModel):
    """Resident medical record entry."""

    class RecordType(models.TextChoices):
        DIAGNOSIS = "diagnosis", "Diagnosis"
        LAB_RESULT = "lab_result", "Lab Result"
        IMAGING = "imaging", "Imaging"
        PRESCRIPTION = "prescription", "Prescription"
        VACCINATION = "vaccination", "Vaccination"
        NOTE = "note", "Clinical Note"

    resident = models.ForeignKey("residents.ResidentProfile", on_delete=models.CASCADE, related_name="medical_records")
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True)
    record_type = models.CharField(max_length=20, choices=RecordType.choices, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    record_date = models.DateField(default=timezone.now, db_index=True)
    provider_name = models.CharField(max_length=255, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    is_confidential = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "healthcare_medical_record"
        indexes = [
            models.Index(fields=["estate", "resident", "record_type"]),
            models.Index(fields=["record_date"]),
        ]
