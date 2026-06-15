from django.db import models
from django.utils import timezone

from core.models import TenantBaseModel


class FeeType(TenantBaseModel):
    """Configurable fee type for estate billing."""

    class Frequency(models.TextChoices):
        ONE_TIME = "one_time", "One Time"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        ANNUAL = "annual", "Annual"

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, db_index=True)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=Frequency.choices, default=Frequency.MONTHLY)
    is_mandatory = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, db_index=True)
    gl_code = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = "billing_fee_type"
        unique_together = [("estate", "code")]
        indexes = [
            models.Index(fields=["estate", "is_active"]),
        ]


class Invoice(TenantBaseModel):
    """Billing invoice for a unit/resident."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        PARTIAL = "partial", "Partially Paid"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        CANCELLED = "cancelled", "Cancelled"
        WRITTEN_OFF = "written_off", "Written Off"

    invoice_number = models.CharField(max_length=50, db_index=True)
    unit = models.ForeignKey("estates.Unit", on_delete=models.CASCADE, related_name="invoices")
    resident = models.ForeignKey(
        "residents.ResidentProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField(db_index=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="NGN")
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "billing_invoice"
        unique_together = [("estate", "invoice_number")]
        indexes = [
            models.Index(fields=["estate", "status", "due_date"]),
            models.Index(fields=["unit", "status"]),
            models.Index(fields=["due_date", "status"]),
        ]

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid


class InvoiceLine(TenantBaseModel):
    """Line item on an invoice."""

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="lines")
    fee_type = models.ForeignKey(FeeType, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "billing_invoice_line"
        indexes = [
            models.Index(fields=["invoice"]),
            models.Index(fields=["estate", "invoice"]),
        ]


class Payment(TenantBaseModel):
    """Payment record against an invoice."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    class Method(models.TextChoices):
        CARD = "card", "Card"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        USSD = "ussd", "USSD"
        WALLET = "wallet", "Wallet"
        CASH = "cash", "Cash"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    payer = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="payments")
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    provider_reference = models.CharField(max_length=255, blank=True, db_index=True)
    provider = models.CharField(max_length=50, blank=True)
    method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="NGN")
    paid_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "billing_payment"
        indexes = [
            models.Index(fields=["estate", "status", "created_at"]),
            models.Index(fields=["invoice", "status"]),
            models.Index(fields=["reference"]),
        ]


class DebtRecord(TenantBaseModel):
    """Outstanding debt tracking for a unit."""

    class Status(models.TextChoices):
        CURRENT = "current", "Current"
        OVERDUE = "overdue", "Overdue"
        IN_COLLECTION = "in_collection", "In Collection"
        SETTLED = "settled", "Settled"
        WRITTEN_OFF = "written_off", "Written Off"

    unit = models.ForeignKey("estates.Unit", on_delete=models.CASCADE, related_name="debts")
    resident = models.ForeignKey(
        "residents.ResidentProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="debts",
    )
    total_debt = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    overdue_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    oldest_due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CURRENT, db_index=True)
    last_payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "billing_debt_record"
        indexes = [
            models.Index(fields=["estate", "status"]),
            models.Index(fields=["unit", "status"]),
        ]
