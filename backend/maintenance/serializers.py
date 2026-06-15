from core.serializers import TenantModelSerializer
from maintenance.models import SLAConfig, Ticket, TicketComment


class SLAConfigSerializer(TenantModelSerializer):
    class Meta:
        model = SLAConfig
        fields = [
            "id",
            "estate",
            "name",
            "priority",
            "category",
            "response_time_hours",
            "resolution_time_hours",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class TicketSerializer(TenantModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id",
            "estate",
            "ticket_number",
            "title",
            "description",
            "category",
            "priority",
            "status",
            "unit",
            "reported_by",
            "assigned_to",
            "sla_config",
            "due_at",
            "resolved_at",
            "attachments",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]


class TicketCommentSerializer(TenantModelSerializer):
    class Meta:
        model = TicketComment
        fields = [
            "id",
            "estate",
            "ticket",
            "author",
            "body",
            "is_internal",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estate", "created_at", "updated_at"]
