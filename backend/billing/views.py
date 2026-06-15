import uuid

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from billing.models import DebtRecord, FeeType, Invoice, Payment
from billing.serializers import (
    DebtRecordSerializer,
    FeeTypeSerializer,
    InvoicePaySerializer,
    InvoiceSerializer,
    PaymentSerializer,
)
from core.viewsets import TenantViewSet


class FeeTypeViewSet(TenantViewSet):
    queryset = FeeType.objects.all()
    serializer_class = FeeTypeSerializer
    filterset_fields = ["frequency", "is_mandatory", "is_active"]
    search_fields = ["name", "code"]


class InvoiceViewSet(TenantViewSet):
    queryset = Invoice.objects.select_related("unit", "resident__user")
    serializer_class = InvoiceSerializer
    filterset_fields = ["unit", "resident", "status"]
    search_fields = ["invoice_number", "notes"]

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        with transaction.atomic():
            invoice = self.get_queryset().select_for_update().get(pk=pk)
            if invoice.estate_id != getattr(request, "estate_id", None) and not request.user.is_superuser:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

            if invoice.status in (Invoice.Status.PAID, Invoice.Status.CANCELLED, Invoice.Status.WRITTEN_OFF):
                return Response(
                    {"detail": f"Invoice is already {invoice.status}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            pay_serializer = InvoicePaySerializer(data=request.data)
            pay_serializer.is_valid(raise_exception=True)

            balance_due = invoice.balance_due
            if balance_due <= 0:
                return Response({"detail": "Invoice is already fully paid."}, status=status.HTTP_400_BAD_REQUEST)

            requested_amount = pay_serializer.validated_data.get("amount")
            # Explicitly check for None (Decimal("0") is falsy in Python)
            if requested_amount is not None:
                if requested_amount <= 0:
                    return Response({"detail": "Invalid payment amount."}, status=status.HTTP_400_BAD_REQUEST)
                # Cap payment at balance_due to prevent overpayment
                amount = min(requested_amount, balance_due)
            else:
                amount = balance_due

            payment = Payment.objects.create(
                estate_id=invoice.estate_id,
                invoice=invoice,
                payer=request.user,
                reference=f"PAY-{uuid.uuid4().hex[:12].upper()}",
                method=pay_serializer.validated_data["method"],
                provider=pay_serializer.validated_data.get("provider", ""),
                status=Payment.Status.COMPLETED,
                amount=amount,
                currency=invoice.currency,
                paid_at=timezone.now(),
            )

            invoice.amount_paid += amount
            if invoice.amount_paid >= invoice.total_amount:
                invoice.status = Invoice.Status.PAID
            else:
                invoice.status = Invoice.Status.PARTIAL
            invoice.save(update_fields=["amount_paid", "status", "updated_at"])

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentViewSet(TenantViewSet):
    queryset = Payment.objects.select_related("invoice", "payer")
    serializer_class = PaymentSerializer
    filterset_fields = ["invoice", "payer", "status", "method", "provider"]
    search_fields = ["reference", "provider_reference"]


class DebtRecordViewSet(TenantViewSet):
    queryset = DebtRecord.objects.select_related("unit", "resident__user")
    serializer_class = DebtRecordSerializer
    filterset_fields = ["unit", "resident", "status"]
    search_fields = ["notes"]
