from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from core.viewsets import TenantViewSet
from notifications.models import Notification, NotificationPreference
from notifications.serializers import NotificationPreferenceSerializer, NotificationSerializer


class NotificationViewSet(TenantViewSet):
    serializer_class = NotificationSerializer
    filterset_fields = ["channel", "status", "priority"]
    search_fields = ["title", "body", "external_id"]

    def get_queryset(self):
        qs = Notification.objects.select_related("recipient")
        estate_id = getattr(self.request, "estate_id", None)
        if self.request.user.is_superuser and not estate_id:
            return qs
        if not estate_id:
            return qs.none()
        # Non-superusers can only see their own notifications
        if not self.request.user.is_superuser:
            return qs.filter(estate_id=estate_id, recipient=self.request.user)
        return qs.filter(estate_id=estate_id)

    def perform_create(self, serializer):
        estate_id = getattr(self.request, "estate_id", None)
        if not estate_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "X-Estate-Id header is required."})
        serializer.save(estate_id=estate_id)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.status = Notification.Status.READ
        notification.read_at = timezone.now()
        notification.save(update_fields=["status", "read_at", "updated_at"])
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Mark all of the current user's notifications as read."""
        estate_id = getattr(request, "estate_id", None)
        if not estate_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "X-Estate-Id header is required."})
        updated = Notification.objects.filter(
            estate_id=estate_id,
            recipient=request.user,
            status__in=[Notification.Status.PENDING, Notification.Status.SENT, Notification.Status.DELIVERED],
        ).update(status=Notification.Status.READ, read_at=timezone.now())
        return Response({"marked_read": updated})


class NotificationPreferenceViewSet(TenantViewSet):
    serializer_class = NotificationPreferenceSerializer
    filterset_fields = ["channel", "category", "is_enabled"]

    def get_queryset(self):
        qs = NotificationPreference.objects.select_related("user")
        estate_id = getattr(self.request, "estate_id", None)
        if self.request.user.is_superuser and not estate_id:
            return qs
        if not estate_id:
            return qs.none()
        if not self.request.user.is_superuser:
            return qs.filter(estate_id=estate_id, user=self.request.user)
        return qs.filter(estate_id=estate_id)
