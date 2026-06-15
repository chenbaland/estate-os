from core.viewsets import TenantViewSet
from utilities.models import ConsumptionRecord, UtilityAccount, UtilityTransaction
from utilities.serializers import (
    ConsumptionRecordSerializer,
    UtilityAccountSerializer,
    UtilityTransactionSerializer,
)


class UtilityAccountViewSet(TenantViewSet):
    queryset = UtilityAccount.objects.all()
    serializer_class = UtilityAccountSerializer
    filterset_fields = ["unit", "utility_type", "status"]
    search_fields = ["account_number", "meter_number", "provider_name"]


class UtilityTransactionViewSet(TenantViewSet):
    queryset = UtilityTransaction.objects.all()
    serializer_class = UtilityTransactionSerializer
    filterset_fields = ["account", "user", "transaction_type", "status"]
    search_fields = ["reference", "provider_reference", "token"]


class ConsumptionRecordViewSet(TenantViewSet):
    queryset = ConsumptionRecord.objects.all()
    serializer_class = ConsumptionRecordSerializer
    filterset_fields = ["account", "is_estimated", "recorded_by"]
    search_fields = ["notes"]
