from django.db import models

from core.models import TenantBaseModel


class ResidentProfile(TenantBaseModel):
    """Primary resident profile linked to a user and unit."""

    class ResidentType(models.TextChoices):
        OWNER = "owner", "Owner"
        TENANT = "tenant", "Tenant"
        FAMILY = "family", "Family Member"
        STAFF = "staff", "Staff"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        PENDING = "pending", "Pending Approval"
        SUSPENDED = "suspended", "Suspended"

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="resident_profiles")
    unit = models.ForeignKey(
        "estates.Unit",
        on_delete=models.CASCADE,
        related_name="residents",
        null=True,
        blank=True,
    )
    resident_type = models.CharField(
        max_length=20,
        choices=ResidentType.choices,
        blank=True,
        default="",
        db_index=True,
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    move_in_date = models.DateField(null=True, blank=True)
    move_out_date = models.DateField(null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    id_document_type = models.CharField(max_length=50, blank=True)
    id_document_number = models.CharField(max_length=100, blank=True)
    id_document_file = models.FileField(upload_to="residents/documents/%Y/%m/", blank=True, null=True)
    is_primary = models.BooleanField(default=False, db_index=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "residents_profile"
        indexes = [
            models.Index(fields=["estate", "user", "status"]),
            models.Index(fields=["estate", "unit", "is_primary"]),
            models.Index(fields=["resident_type", "status"]),
        ]

    def __str__(self):
        unit_label = self.unit.unit_number if self.unit_id else "unassigned"
        return f"{self.user.email} @ {unit_label}"


class FamilyMember(TenantBaseModel):
    """Family member linked to a primary resident."""

    class Relationship(models.TextChoices):
        SPOUSE = "spouse", "Spouse"
        CHILD = "child", "Child"
        PARENT = "parent", "Parent"
        SIBLING = "sibling", "Sibling"
        OTHER = "other", "Other"

    primary_resident = models.ForeignKey(
        ResidentProfile,
        on_delete=models.CASCADE,
        related_name="family_members",
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="family_memberships",
    )
    full_name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=20, choices=Relationship.choices)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    photo = models.ImageField(upload_to="residents/family/%Y/%m/", blank=True, null=True)
    has_gate_access = models.BooleanField(default=False)
    access_expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "residents_family_member"
        indexes = [
            models.Index(fields=["estate", "primary_resident", "is_active"]),
        ]


class DomesticStaff(TenantBaseModel):
    """Domestic staff employed by a resident household."""

    class StaffRole(models.TextChoices):
        NANNY = "nanny", "Nanny"
        DRIVER = "driver", "Driver"
        COOK = "cook", "Cook"
        CLEANER = "cleaner", "Cleaner"
        GARDENER = "gardener", "Gardener"
        SECURITY = "security", "Security"
        OTHER = "other", "Other"

    employer = models.ForeignKey(
        ResidentProfile,
        on_delete=models.CASCADE,
        related_name="domestic_staff",
    )
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=StaffRole.choices)
    phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to="residents/staff/%Y/%m/", blank=True, null=True)
    id_document_number = models.CharField(max_length=100, blank=True)
    has_gate_access = models.BooleanField(default=True)
    access_schedule = models.JSONField(default=dict, blank=True)
    employment_start = models.DateField(null=True, blank=True)
    employment_end = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "residents_domestic_staff"
        indexes = [
            models.Index(fields=["estate", "employer", "is_active"]),
        ]


class Vehicle(TenantBaseModel):
    """Resident-registered vehicle for gate access and parking."""

    class VehicleType(models.TextChoices):
        CAR = "car", "Car"
        SUV = "suv", "SUV"
        MOTORCYCLE = "motorcycle", "Motorcycle"
        TRUCK = "truck", "Truck"
        EV = "ev", "Electric Vehicle"

    owner = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name="vehicles")
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.choices, default=VehicleType.CAR)
    make = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    license_plate = models.CharField(max_length=20, db_index=True)
    registration_number = models.CharField(max_length=50, blank=True)
    registration_expiry = models.DateField(null=True, blank=True)
    rfid_tag = models.CharField(max_length=100, blank=True, db_index=True)
    is_ev = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    photo = models.ImageField(upload_to="residents/vehicles/%Y/%m/", blank=True, null=True)

    class Meta:
        db_table = "residents_vehicle"
        unique_together = [("estate", "license_plate")]
        indexes = [
            models.Index(fields=["estate", "owner", "is_active"]),
            models.Index(fields=["license_plate"]),
        ]
