from core.viewsets import TenantViewSet
from facilities.models import BlackoutDate, Booking, Facility
from facilities.serializers import BlackoutDateSerializer, BookingSerializer, FacilitySerializer


class FacilityViewSet(TenantViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    filterset_fields = ["facility_type", "is_active", "requires_approval"]
    search_fields = ["name", "slug", "location"]


class BookingViewSet(TenantViewSet):
    queryset = Booking.objects.select_related("facility", "user", "resident__user")
    serializer_class = BookingSerializer
    filterset_fields = ["facility", "user", "resident", "status"]
    search_fields = ["payment_reference", "notes"]


class BlackoutDateViewSet(TenantViewSet):
    queryset = BlackoutDate.objects.select_related("facility")
    serializer_class = BlackoutDateSerializer
    filterset_fields = ["facility", "is_recurring_yearly"]
    search_fields = ["reason"]
