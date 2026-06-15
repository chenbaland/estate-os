import json
import logging

from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.viewsets import TenantViewSet
from payments.models import PaymentProviderConfig, PaymentTransaction
from payments.providers.flutterwave import FlutterwaveProvider
from payments.providers.paystack import PaystackProvider
from payments.providers.stripe import StripeProvider
from payments.serializers import PaymentProviderConfigSerializer, PaymentTransactionSerializer

logger = logging.getLogger("estateos.payments.webhooks")


class PaymentProviderConfigViewSet(TenantViewSet):
    queryset = PaymentProviderConfig.objects.all()
    serializer_class = PaymentProviderConfigSerializer
    filterset_fields = ["provider", "is_default", "is_active"]


class PaymentTransactionViewSet(TenantViewSet):
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    filterset_fields = ["provider_config", "user", "status", "related_object_type"]
    search_fields = ["reference", "provider_reference", "description"]


def _update_transaction_from_webhook(reference, provider_status, provider_reference="", raw_response=None):
    if not reference:
        return None
    try:
        transaction = PaymentTransaction.objects.get(reference=reference)
    except PaymentTransaction.DoesNotExist:
        logger.warning("Webhook received for unknown reference: %s", reference)
        return None

    if provider_status in ("success", "successful", "completed", "charge.success"):
        transaction.status = PaymentTransaction.Status.SUCCESS
        transaction.paid_at = timezone.now()
    elif provider_status in ("failed", "failure", "charge.failed"):
        transaction.status = PaymentTransaction.Status.FAILED
    else:
        transaction.status = PaymentTransaction.Status.PENDING

    if provider_reference:
        transaction.provider_reference = provider_reference
    if raw_response:
        transaction.provider_response = raw_response
    transaction.save(update_fields=["status", "paid_at", "provider_reference", "provider_response", "updated_at"])
    return transaction


@method_decorator(csrf_exempt, name="dispatch")
class PaystackWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        signature = request.META.get("HTTP_X_PAYSTACK_SIGNATURE", "")
        provider = PaystackProvider()
        body = request.body
        if not provider.validate_webhook_signature(body, signature):
            return Response({"detail": "Invalid signature."}, status=status.HTTP_400_BAD_REQUEST)

        payload = json.loads(body.decode("utf-8")) if body else request.data
        event = provider.parse_webhook_event(payload)
        data = event.get("data", {})
        reference = data.get("reference", "")
        txn_status = data.get("status", event.get("event", ""))
        _update_transaction_from_webhook(reference, txn_status, str(data.get("id", "")), payload)
        return Response({"status": "ok"})


@method_decorator(csrf_exempt, name="dispatch")
class FlutterwaveWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        signature = request.META.get("HTTP_VERIF_HASH", "")
        provider = FlutterwaveProvider()
        body = request.body
        # Always validate signature if secret is configured; reject missing signatures
        if not provider.validate_webhook_signature(body, signature):
            return Response({"detail": "Invalid signature."}, status=status.HTTP_400_BAD_REQUEST)

        payload = request.data
        event = provider.parse_webhook_event(payload)
        data = event.get("data", {})
        reference = data.get("tx_ref") or data.get("reference", "")
        txn_status = data.get("status", event.get("event", ""))
        _update_transaction_from_webhook(reference, txn_status, str(data.get("id", "")), payload)
        return Response({"status": "ok"})


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        provider = StripeProvider()
        body = request.body
        # Always validate signature if webhook secret is configured
        if not provider.validate_webhook_signature(body, signature):
            return Response({"detail": "Invalid signature."}, status=status.HTTP_400_BAD_REQUEST)

        payload = json.loads(body.decode("utf-8")) if body else request.data
        event = provider.parse_webhook_event(payload)
        data = event.get("data", {}).get("object", event.get("data", {}))
        reference = data.get("client_reference_id") or data.get("metadata", {}).get("reference", "")
        txn_status = data.get("status", event.get("type", ""))
        _update_transaction_from_webhook(reference, txn_status, data.get("id", ""), payload)
        return Response({"status": "ok"})
