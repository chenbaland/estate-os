from django.db import models

from core.models import TenantBaseModel


class PaymentProviderConfig(TenantBaseModel):
    """Estate-level payment provider configuration."""

    class Provider(models.TextChoices):
        PAYSTACK = "paystack", "Paystack"
        FLUTTERWAVE = "flutterwave", "Flutterwave"
        STRIPE = "stripe", "Stripe"

    provider = models.CharField(max_length=20, choices=Provider.choices, db_index=True)
    is_default = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    public_key = models.CharField(max_length=255, blank=True)
    secret_key_encrypted = models.TextField(blank=True)
    webhook_secret = models.CharField(max_length=255, blank=True)
    supported_currencies = models.JSONField(default=list)
    supported_methods = models.JSONField(default=list)
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "payments_provider_config"
        unique_together = [("estate", "provider")]
        indexes = [
            models.Index(fields=["estate", "is_active", "is_default"]),
        ]


class PaymentTransaction(TenantBaseModel):
    """Payment transaction processed through a provider."""

    class Status(models.TextChoices):
        INITIATED = "initiated", "Initiated"
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"
        DISPUTED = "disputed", "Disputed"

    provider_config = models.ForeignKey(
        PaymentProviderConfig,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    user = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="payment_transactions")
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    provider_reference = models.CharField(max_length=255, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED, db_index=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="NGN")
    description = models.CharField(max_length=500, blank=True)
    callback_url = models.URLField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    related_object_type = models.CharField(max_length=100, blank=True)
    related_object_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "payments_transaction"
        indexes = [
            models.Index(fields=["estate", "status", "created_at"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["reference"]),
            models.Index(fields=["related_object_type", "related_object_id"]),
        ]
