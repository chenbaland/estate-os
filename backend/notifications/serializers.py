from core.serializers import TenantModelSerializer
from notifications.models import Notification, NotificationPreference


class NotificationSerializer(TenantModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "estate",
            "recipient",
            "template",
            "channel",
            "status",
            "priority",
            "title",
            "body",
            "data",
            "action_url",
            "sent_at",
            "delivered_at",
            "read_at",
            "error_message",
            "external_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class NotificationPreferenceSerializer(TenantModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            "id",
            "estate",
            "user",
            "channel",
            "category",
            "is_enabled",
            "quiet_hours_start",
            "quiet_hours_end",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
