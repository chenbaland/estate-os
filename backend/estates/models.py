from django.db import models

from core.models import BaseModel


class Estate(BaseModel):
    """Top-level tenant representing a managed estate or community."""

    class EstateType(models.TextChoices):
        GATED = "gated", "Gated Community"
        MIXED_USE = "mixed_use", "Mixed Use"
        APARTMENT = "apartment", "Apartment Complex"
        TOWNHOUSE = "townhouse", "Townhouse Estate"
        COMMERCIAL = "commercial", "Commercial Estate"

    class Tier(models.TextChoices):
        STANDARD = "standard", "Standard"
        PREMIUM = "premium", "Premium"
        ENTERPRISE = "enterprise", "Enterprise"

    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    estate_type = models.CharField(max_length=20, choices=EstateType.choices, default=EstateType.GATED)
    tier = models.CharField(max_length=20, choices=Tier.choices, default=Tier.STANDARD)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="estates/logos/", blank=True, null=True)
    cover_image = models.ImageField(upload_to="estates/covers/", blank=True, null=True)

    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=2, default="NG")
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    custom_domain = models.CharField(max_length=255, blank=True, unique=True, null=True)

    timezone = models.CharField(max_length=50, default="Africa/Lagos")
    currency = models.CharField(max_length=3, default="NGN")
    locale = models.CharField(max_length=10, default="en-NG")

    total_units = models.PositiveIntegerField(default=0)
    occupied_units = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    settings = models.JSONField(default=dict, blank=True)
    feature_flags = models.JSONField(default=dict, blank=True)

    onboarded_at = models.DateTimeField(null=True, blank=True)
    subscription_expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "estates_estate"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug", "is_active"]),
            models.Index(fields=["city", "country"]),
            models.Index(fields=["is_active", "is_deleted"]),
        ]

    def __str__(self):
        return self.name


class Block(BaseModel):
    """Physical block or wing within an estate."""

    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, related_name="blocks")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, db_index=True)
    description = models.TextField(blank=True)
    floor_count = models.PositiveSmallIntegerField(default=1)
    unit_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "estates_block"
        unique_together = [("estate", "code")]
        indexes = [
            models.Index(fields=["estate", "is_active"]),
        ]

    def __str__(self):
        return f"{self.estate.name} - {self.name}"


class Unit(BaseModel):
    """Individual residential or commercial unit."""

    class UnitType(models.TextChoices):
        APARTMENT = "apartment", "Apartment"
        HOUSE = "house", "House"
        TOWNHOUSE = "townhouse", "Townhouse"
        PENTHOUSE = "penthouse", "Penthouse"
        COMMERCIAL = "commercial", "Commercial"
        STUDIO = "studio", "Studio"

    class OccupancyStatus(models.TextChoices):
        VACANT = "vacant", "Vacant"
        OCCUPIED = "occupied", "Occupied"
        RESERVED = "reserved", "Reserved"
        MAINTENANCE = "maintenance", "Under Maintenance"

    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, related_name="units")
    block = models.ForeignKey(Block, on_delete=models.SET_NULL, null=True, blank=True, related_name="units")
    unit_number = models.CharField(max_length=50, db_index=True)
    unit_type = models.CharField(max_length=20, choices=UnitType.choices, default=UnitType.APARTMENT)
    floor = models.SmallIntegerField(default=0)
    bedrooms = models.PositiveSmallIntegerField(default=1)
    bathrooms = models.PositiveSmallIntegerField(default=1)
    square_meters = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    occupancy_status = models.CharField(
        max_length=20,
        choices=OccupancyStatus.choices,
        default=OccupancyStatus.VACANT,
        db_index=True,
    )
    owner = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_units",
    )
    monthly_service_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "estates_unit"
        unique_together = [("estate", "unit_number")]
        indexes = [
            models.Index(fields=["estate", "occupancy_status"]),
            models.Index(fields=["estate", "block", "unit_number"]),
            models.Index(fields=["owner"]),
        ]

    def __str__(self):
        return f"{self.estate.slug}/{self.unit_number}"
