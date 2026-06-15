from core.serializers import TenantModelSerializer
from transportation.models import RideRequest


class RideRequestSerializer(TenantModelSerializer):
    class Meta:
        model = RideRequest
        fields = [
            "id",
            "estate",
            "requester",
            "status",
            "ride_type",
            "pickup_address",
            "dropoff_address",
            "pickup_latitude",
            "pickup_longitude",
            "dropoff_latitude",
            "dropoff_longitude",
            "scheduled_at",
            "driver_name",
            "driver_phone",
            "vehicle_description",
            "estimated_fare",
            "actual_fare",
            "currency",
            "payment_reference",
            "started_at",
            "completed_at",
            "cancelled_at",
            "cancellation_reason",
            "passenger_count",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
