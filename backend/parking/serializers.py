from core.serializers import TenantModelSerializer
from parking.models import EVChargingSession, ParkingPermit, ParkingSlot


class ParkingSlotSerializer(TenantModelSerializer):
    class Meta:
        model = ParkingSlot
        fields = [
            "id",
            "estate",
            "slot_number",
            "slot_type",
            "status",
            "location",
            "block",
            "unit",
            "has_ev_charger",
            "is_covered",
            "monthly_rate",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class ParkingPermitSerializer(TenantModelSerializer):
    class Meta:
        model = ParkingPermit
        fields = [
            "id",
            "estate",
            "slot",
            "vehicle",
            "resident",
            "permit_number",
            "status",
            "valid_from",
            "valid_until",
            "qr_code",
            "monthly_fee",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class EVChargingSessionSerializer(TenantModelSerializer):
    class Meta:
        model = EVChargingSession
        fields = [
            "id",
            "estate",
            "slot",
            "vehicle",
            "resident",
            "status",
            "started_at",
            "ended_at",
            "energy_kwh",
            "cost",
            "currency",
            "charger_id",
            "payment_reference",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
