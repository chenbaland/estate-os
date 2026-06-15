from django.db import models

from core.models import TenantBaseModel


class Vendor(TenantBaseModel):
    """Marketplace vendor operating within an estate."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Approval"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        CLOSED = "closed", "Closed"

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="vendor_profiles")
    business_name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="marketplace/vendors/%Y/%m/", blank=True, null=True)
    cover_image = models.ImageField(upload_to="marketplace/vendors/covers/%Y/%m/", blank=True, null=True)
    category = models.CharField(max_length=100, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.PositiveIntegerField(default=0)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10)
    operating_hours = models.JSONField(default=dict, blank=True)
    is_verified = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "marketplace_vendor"
        unique_together = [("estate", "slug")]
        indexes = [
            models.Index(fields=["estate", "status", "category"]),
            models.Index(fields=["business_name"]),
        ]


class Product(TenantBaseModel):
    """Product listing in the marketplace."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        OUT_OF_STOCK = "out_of_stock", "Out of Stock"
        DISCONTINUED = "discontinued", "Discontinued"

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=150)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="NGN")
    sku = models.CharField(max_length=100, blank=True, db_index=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    images = models.JSONField(default=list, blank=True)
    attributes = models.JSONField(default=dict, blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "marketplace_product"
        unique_together = [("vendor", "slug")]
        indexes = [
            models.Index(fields=["estate", "status", "category"]),
            models.Index(fields=["vendor", "status"]),
        ]


class Cart(TenantBaseModel):
    """Shopping cart for a user."""

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="carts")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="carts")
    items = models.JSONField(default=list)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "marketplace_cart"
        indexes = [
            models.Index(fields=["estate", "user", "is_active"]),
        ]


class Order(TenantBaseModel):
    """Marketplace order."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PREPARING = "preparing", "Preparing"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for Delivery"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    order_number = models.CharField(max_length=50, db_index=True)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="marketplace_orders")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    items = models.JSONField(default=list)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="NGN")
    delivery_address = models.TextField(blank=True)
    unit = models.ForeignKey("estates.Unit", on_delete=models.SET_NULL, null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "marketplace_order"
        unique_together = [("estate", "order_number")]
        indexes = [
            models.Index(fields=["estate", "status", "created_at"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["vendor", "status"]),
        ]


class Review(TenantBaseModel):
    """Product or vendor review."""

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="marketplace_reviews")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name="reviews")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)
    is_verified_purchase = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "marketplace_review"
        indexes = [
            models.Index(fields=["estate", "vendor", "is_visible"]),
            models.Index(fields=["product", "rating"]),
        ]
