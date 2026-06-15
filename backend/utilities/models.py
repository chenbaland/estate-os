from django.db import models
from django.utils import timezone

from core.models import TenantBaseModel


class UtilityAccount(TenantBaseModel):
    """Utility meter account for a unit."""

    class UtilityType(models.TextChoices):
        ELECTRICITY = "electricity", "Electricity"
        WATER = "water", "Water"
        GAS = "gas", "Gas"
        INTERNET = "internet", "Internet"
        WASTE = "waste", "Waste Management"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        DISCONNECTED = "disconnected", "Disconnected"

    unit = models.ForeignKey("estates.Unit", on_delete=models.CASCADE, related_name="utility_accounts")
    utility_type = models.CharField(max_length=20, choices=UtilityType.choices, db_index=True)
    account_number = models.CharField(max_length=100, db_index=True)
    meter_number = models.CharField(max_length=100, blank=True)
    provider_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    current_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    last_reading = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    last_reading_date = models.DateField(null=True, blank=True)
    tariff_plan = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "utilities_account"
        unique_together = [("estate", "utility_type", "account_number")]
        indexes = [
            models.Index(fields=["estate", "utility_type", "status"]),
            models.Index(fields=["unit", "utility_type"]),
        ]


class UtilityTransaction(TenantBaseModel):
    """Token purchase or payment transaction for utilities."""

    class TransactionType(models.TextChoices):
        PURCHASE = "purchase", "Token Purchase"
        PAYMENT = "payment", "Bill Payment"
        REFUND = "refund", "Refund"
        ADJUSTMENT = "adjustment", "Adjustment"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    account = models.ForeignKey(UtilityAccount, on_delete=models.CASCADE, related_name="transactions")
    user = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    units_purchased = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    token = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    provider_reference = models.CharField(max_length=255, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "utilities_transaction"
        indexes = [
            models.Index(fields=["estate", "status", "created_at"]),
            models.Index(fields=["account", "transaction_type"]),
        ]


class ConsumptionRecord(TenantBaseModel):
    """Periodic utility consumption reading."""

    account = models.ForeignKey(UtilityAccount, on_delete=models.CASCADE, related_name="consumption_records")
    reading_date = models.DateField(default=timezone.now, db_index=True)
    previous_reading = models.DecimalField(max_digits=14, decimal_places=4)
    current_reading = models.DecimalField(max_digits=14, decimal_places=4)
    consumption = models.DecimalField(max_digits=14, decimal_places=4)
    cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    recorded_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    is_estimated = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "utilities_consumption_record"
        indexes = [
            models.Index(fields=["estate", "account", "reading_date"]),
            models.Index(fields=["reading_date"]),
        ]
