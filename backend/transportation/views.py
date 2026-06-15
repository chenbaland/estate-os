from core.viewsets import TenantViewSet
from transportation.models import RideRequest
from transportation.serializers import RideRequestSerializer


class RideRequestViewSet(TenantViewSet):
    queryset = RideRequest.objects.select_related("requester")
    serializer_class = RideRequestSerializer
    filterset_fields = ["requester", "status", "ride_type"]
    search_fields = ["pickup_address", "dropoff_address", "driver_name", "payment_reference"]
