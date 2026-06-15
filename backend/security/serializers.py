from core.serializers import TenantModelSerializer
from security.models import EmergencyBroadcast, Incident, PatrolLog, SOSAlert


class IncidentSerializer(TenantModelSerializer):
    class Meta:
        model = Incident
        fields = [
            "id",
            "estate",
            "title",
            "description",
            "category",
            "severity",
            "status",
            "location",
            "latitude",
            "longitude",
            "reported_by",
            "assigned_to",
            "occurred_at",
            "resolved_at",
            "resolution_notes",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class PatrolLogSerializer(TenantModelSerializer):
    class Meta:
        model = PatrolLog
        fields = [
            "id",
            "estate",
            "officer",
            "route_name",
            "checkpoint",
            "status",
            "checked_at",
            "latitude",
            "longitude",
            "notes",
            "photo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class SOSAlertSerializer(TenantModelSerializer):
    class Meta:
        model = SOSAlert
        fields = [
            "id",
            "estate",
            "resident",
            "status",
            "message",
            "latitude",
            "longitude",
            "location_description",
            "acknowledged_by",
            "acknowledged_at",
            "resolved_at",
            "response_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class EmergencyBroadcastSerializer(TenantModelSerializer):
    class Meta:
        model = EmergencyBroadcast
        fields = [
            "id",
            "estate",
            "title",
            "message",
            "priority",
            "channel",
            "sent_by",
            "sent_at",
            "expires_at",
            "is_active",
            "recipient_count",
            "delivery_stats",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
