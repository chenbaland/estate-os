from core.viewsets import TenantViewSet
from parking.models import EVChargingSession, ParkingPermit, ParkingSlot
from parking.serializers import (
    EVChargingSessionSerializer,
    ParkingPermitSerializer,
    ParkingSlotSerializer,
)


class ParkingSlotViewSet(TenantViewSet):
    queryset = ParkingSlot.objects.select_related("unit")
    serializer_class = ParkingSlotSerializer
    filterset_fields = ["slot_type", "status", "block", "unit", "has_ev_charger"]
    search_fields = ["slot_number", "location"]


class ParkingPermitViewSet(TenantViewSet):
    queryset = ParkingPermit.objects.select_related("slot", "vehicle", "resident__user")
    serializer_class = ParkingPermitSerializer
    filterset_fields = ["slot", "vehicle", "resident", "status"]
    search_fields = ["permit_number", "qr_code"]


class EVChargingSessionViewSet(TenantViewSet):
    queryset = EVChargingSession.objects.select_related("slot", "vehicle", "resident__user")
    serializer_class = EVChargingSessionSerializer
    filterset_fields = ["slot", "vehicle", "resident", "status"]
    search_fields = ["charger_id", "payment_reference"]
