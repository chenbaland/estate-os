from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.membership import activate_resident_profile
from core.permissions import IsEstateAdmin
from core.viewsets import TenantViewSet
from estates.models import Unit
from notifications.models import Notification, NotificationTemplate
from residents.models import DomesticStaff, FamilyMember, ResidentProfile, Vehicle
from residents.serializers import (
    DomesticStaffSerializer,
    FamilyMemberSerializer,
    ResidentProfileSerializer,
    VehicleSerializer,
)


class ResidentProfileViewSet(TenantViewSet):
    queryset = ResidentProfile.objects.select_related("user", "unit", "estate")
    serializer_class = ResidentProfileSerializer
    filterset_fields = ["user", "unit", "resident_type", "status", "is_primary"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "notes"]

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsEstateAdmin],
    )
    def activate(self, request, pk=None):
        profile = self.get_object()
        unit = None
        unit_id = request.data.get("unit_id")
        resident_type = request.data.get("resident_type")
        if unit_id:
            try:
                unit = Unit.objects.get(id=unit_id, estate=profile.estate, is_active=True)
            except Unit.DoesNotExist as exc:
                raise ValidationError({"unit_id": "Select a valid unit in this estate."}) from exc

        if not resident_type:
            raise ValidationError({"resident_type": "Select homeowner or tenant."})

        try:
            profile = activate_resident_profile(
                profile,
                activated_by=request.user,
                resident_type=resident_type,
                unit=unit,
            )
        except ValueError as exc:
            raise ValidationError({"detail": str(exc)}) from exc

        return Response(ResidentProfileSerializer(profile).data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsEstateAdmin],
    )
    def reject(self, request, pk=None):
        profile = self.get_object()
        if profile.status != ResidentProfile.Status.PENDING:
            raise ValidationError({"detail": "Only pending profiles can be rejected."})

        reason = request.data.get("reason", "").strip()
        profile.status = ResidentProfile.Status.INACTIVE
        profile.notes = reason or profile.notes
        profile.save(update_fields=["status", "notes", "updated_at"])

        body = f"Your registration request for {profile.estate.name} was not approved."
        if reason:
            body = f"{body} Reason: {reason}"

        Notification.objects.create(
            estate=profile.estate,
            recipient=profile.user,
            channel=NotificationTemplate.Channel.INAPP,
            status=Notification.Status.DELIVERED,
            priority=Notification.Priority.NORMAL,
            title="Resident registration declined",
            body=body,
            data={
                "type": "resident_rejection",
                "resident_profile_id": str(profile.id),
            },
        )
        return Response(ResidentProfileSerializer(profile).data)


class FamilyMemberViewSet(TenantViewSet):
    queryset = FamilyMember.objects.all()
    serializer_class = FamilyMemberSerializer
    filterset_fields = ["primary_resident", "relationship", "is_active", "has_gate_access"]
    search_fields = ["full_name", "phone", "email"]


class DomesticStaffViewSet(TenantViewSet):
    queryset = DomesticStaff.objects.all()
    serializer_class = DomesticStaffSerializer
    filterset_fields = ["employer", "role", "is_active", "has_gate_access"]
    search_fields = ["full_name", "phone"]


class VehicleViewSet(TenantViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    filterset_fields = ["owner", "vehicle_type", "is_ev", "is_active"]
    search_fields = ["license_plate", "make", "model", "rfid_tag"]
