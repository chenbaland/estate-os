from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsTenantMember


class TenantViewSet(viewsets.ModelViewSet):
    """Estate-scoped CRUD viewset. Requires X-Estate-Id header."""

    permission_classes = [IsAuthenticated, IsTenantMember]
    filterset_fields = []
    search_fields = []
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        estate_id = getattr(self.request, "estate_id", None)
        if self.request.user.is_superuser and not estate_id:
            return qs
        if not estate_id:
            return qs.none()
        return qs.filter(estate_id=estate_id)

    def perform_create(self, serializer):
        estate_id = getattr(self.request, "estate_id", None)
        if not estate_id:
            raise ValidationError({"detail": "X-Estate-Id header is required."})
        serializer.save(estate_id=estate_id)


class TenantReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """Estate-scoped read-only viewset."""

    permission_classes = [IsAuthenticated, IsTenantMember]
    filterset_fields = []
    search_fields = []
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        estate_id = getattr(self.request, "estate_id", None)
        if self.request.user.is_superuser and not estate_id:
            return qs
        if not estate_id:
            return qs.none()
        return qs.filter(estate_id=estate_id)
