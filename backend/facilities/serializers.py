from core.serializers import TenantModelSerializer
from facilities.models import BlackoutDate, Booking, Facility


class FacilitySerializer(TenantModelSerializer):
    class Meta:
        model = Facility
        fields = [
            "id",
            "estate",
            "name",
            "slug",
            "facility_type",
            "description",
            "location",
            "capacity",
            "hourly_rate",
            "currency",
            "operating_hours",
            "booking_rules",
            "images",
            "is_active",
            "requires_approval",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class BookingSerializer(TenantModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "estate",
            "facility",
            "user",
            "resident",
            "status",
            "start_time",
            "end_time",
            "guest_count",
            "total_amount",
            "payment_reference",
            "notes",
            "approved_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class BlackoutDateSerializer(TenantModelSerializer):
    class Meta:
        model = BlackoutDate
        fields = [
            "id",
            "estate",
            "facility",
            "start_date",
            "end_date",
            "reason",
            "is_recurring_yearly",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
