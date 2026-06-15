import uuid

from rest_framework import serializers

from billing.models import DebtRecord, FeeType, Invoice, Payment
from core.serializers import TenantModelSerializer


class FeeTypeSerializer(TenantModelSerializer):
    class Meta:
        model = FeeType
        fields = [
            "id",
            "estate",
            "name",
            "code",
            "description",
            "amount",
            "frequency",
            "is_mandatory",
            "is_active",
            "gl_code",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class InvoiceSerializer(TenantModelSerializer):
    balance_due = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "estate",
            "invoice_number",
            "unit",
            "resident",
            "status",
            "issue_date",
            "due_date",
            "subtotal",
            "tax_amount",
            "discount_amount",
            "total_amount",
            "amount_paid",
            "balance_due",
            "currency",
            "notes",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class PaymentSerializer(TenantModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "estate",
            "invoice",
            "payer",
            "reference",
            "provider_reference",
            "provider",
            "method",
            "status",
            "amount",
            "currency",
            "paid_at",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class DebtRecordSerializer(TenantModelSerializer):
    class Meta:
        model = DebtRecord
        fields = [
            "id",
            "estate",
            "unit",
            "resident",
            "total_debt",
            "overdue_amount",
            "oldest_due_date",
            "status",
            "last_payment_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class InvoicePaySerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)
    method = serializers.ChoiceField(choices=Payment.Method.choices, default=Payment.Method.CARD)
    provider = serializers.CharField(required=False, allow_blank=True, default="")
