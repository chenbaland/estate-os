from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from core.viewsets import TenantViewSet
from security.models import EmergencyBroadcast, Incident, PatrolLog, SOSAlert
from security.serializers import (
    EmergencyBroadcastSerializer,
    IncidentSerializer,
    PatrolLogSerializer,
    SOSAlertSerializer,
)


class IncidentViewSet(TenantViewSet):
    queryset = Incident.objects.select_related("reported_by", "assigned_to")
    serializer_class = IncidentSerializer
    filterset_fields = ["category", "severity", "status", "reported_by", "assigned_to"]
    search_fields = ["title", "description", "location"]


class PatrolLogViewSet(TenantViewSet):
    queryset = PatrolLog.objects.select_related("officer")
    serializer_class = PatrolLogSerializer
    filterset_fields = ["officer", "route_name", "checkpoint", "status"]
    search_fields = ["route_name", "checkpoint", "notes"]


class SOSAlertViewSet(TenantViewSet):
    queryset = SOSAlert.objects.select_related("resident__user", "acknowledged_by")
    serializer_class = SOSAlertSerializer
    filterset_fields = ["resident", "status"]
    search_fields = ["message", "location_description"]

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.status = SOSAlert.Status.ACKNOWLEDGED
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save(update_fields=["status", "acknowledged_by", "acknowledged_at", "updated_at"])
        return Response(SOSAlertSerializer(alert).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.status = SOSAlert.Status.RESOLVED
        alert.resolved_at = timezone.now()
        alert.response_notes = request.data.get("response_notes", alert.response_notes)
        alert.save(update_fields=["status", "resolved_at", "response_notes", "updated_at"])
        return Response(SOSAlertSerializer(alert).data)


class EmergencyBroadcastViewSet(TenantViewSet):
    queryset = EmergencyBroadcast.objects.select_related("sent_by")
    serializer_class = EmergencyBroadcastSerializer
    filterset_fields = ["priority", "channel", "is_active"]
    search_fields = ["title", "message"]

    def perform_create(self, serializer):
        estate_id = getattr(self.request, "estate_id", None)
        if not estate_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "X-Estate-Id header is required."})
        serializer.save(estate_id=estate_id, sent_by=self.request.user)
