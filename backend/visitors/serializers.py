import uuid

from rest_framework import serializers

from core.serializers import TenantModelSerializer
from visitors.models import Blacklist, VisitorLog, VisitorPass


class VisitorPassSerializer(TenantModelSerializer):
    qr_code = serializers.CharField(read_only=True)

    class Meta:
        model = VisitorPass
        fields = [
            "id",
            "estate",
            "host",
            "visitor_name",
            "visitor_phone",
            "visitor_email",
            "visitor_company",
            "pass_type",
            "status",
            "qr_code",
            "access_code",
            "valid_from",
            "valid_until",
            "max_entries",
            "entries_used",
            "vehicle_plate",
            "purpose",
            "notes",
            "photo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "qr_code", "entries_used", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["qr_code"] = str(uuid.uuid4())
        return super().create(validated_data)


class VisitorLogSerializer(TenantModelSerializer):
    class Meta:
        model = VisitorLog
        fields = [
            "id",
            "estate",
            "visitor_pass",
            "visitor_name",
            "visitor_phone",
            "host",
            "direction",
            "verification_method",
            "gate_name",
            "vehicle_plate",
            "verified_by",
            "timestamp",
            "photo",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class BlacklistSerializer(TenantModelSerializer):
    class Meta:
        model = Blacklist
        fields = [
            "id",
            "estate",
            "full_name",
            "phone",
            "email",
            "id_document_number",
            "license_plate",
            "photo",
            "reason",
            "description",
            "reported_by",
            "is_active",
            "expires_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class VisitorPassScanSerializer(serializers.Serializer):
    qr_code = serializers.CharField(required=True)
    gate_name = serializers.CharField(required=False, allow_blank=True, default="")
    direction = serializers.ChoiceField(
        choices=VisitorLog.Direction.choices,
        default=VisitorLog.Direction.ENTRY,
    )
