from rest_framework import serializers

from core.serializers import TenantModelSerializer
from payments.models import PaymentProviderConfig, PaymentTransaction


class PaymentProviderConfigSerializer(TenantModelSerializer):
    secret_key_encrypted = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = PaymentProviderConfig
        fields = [
            "id",
            "estate",
            "provider",
            "is_default",
            "is_active",
            "public_key",
            "secret_key_encrypted",
            "webhook_secret",
            "supported_currencies",
            "supported_methods",
            "config",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class PaymentTransactionSerializer(TenantModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            "id",
            "estate",
            "provider_config",
            "user",
            "reference",
            "provider_reference",
            "status",
            "amount",
            "currency",
            "description",
            "callback_url",
            "metadata",
            "provider_response",
            "paid_at",
            "related_object_type",
            "related_object_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
