from core.serializers import TenantModelSerializer
from packages.models import Package, PackageLog


class PackageSerializer(TenantModelSerializer):
    class Meta:
        model = Package
        fields = [
            "id",
            "estate",
            "tracking_number",
            "recipient",
            "unit",
            "package_type",
            "status",
            "carrier",
            "sender_name",
            "description",
            "size",
            "weight_kg",
            "received_at",
            "collected_at",
            "storage_location",
            "photo",
            "otp_code",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class PackageLogSerializer(TenantModelSerializer):
    class Meta:
        model = PackageLog
        fields = [
            "id",
            "estate",
            "package",
            "previous_status",
            "new_status",
            "changed_by",
            "timestamp",
            "notes",
            "location",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
