from core.serializers import TenantModelSerializer
from utilities.models import ConsumptionRecord, UtilityAccount, UtilityTransaction


class UtilityAccountSerializer(TenantModelSerializer):
    class Meta:
        model = UtilityAccount
        fields = [
            "id",
            "estate",
            "unit",
            "utility_type",
            "account_number",
            "meter_number",
            "provider_name",
            "status",
            "current_balance",
            "credit_limit",
            "last_reading",
            "last_reading_date",
            "tariff_plan",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class UtilityTransactionSerializer(TenantModelSerializer):
    class Meta:
        model = UtilityTransaction
        fields = [
            "id",
            "estate",
            "account",
            "user",
            "transaction_type",
            "status",
            "amount",
            "units_purchased",
            "token",
            "reference",
            "provider_reference",
            "completed_at",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class ConsumptionRecordSerializer(TenantModelSerializer):
    class Meta:
        model = ConsumptionRecord
        fields = [
            "id",
            "estate",
            "account",
            "reading_date",
            "previous_reading",
            "current_reading",
            "consumption",
            "cost",
            "recorded_by",
            "is_estimated",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
