from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User, UserRole
from core.permissions import IsSuperAdmin
from estates.models import Estate, Unit
from platform_admin.audit import record_platform_audit
from platform_admin.models import PlatformAuditLog
from platform_admin.serializers import (
    AssignPlatformAdminSerializer,
    PlatformAdminSerializer,
    PlatformAuditLogSerializer,
    PlatformEstateCreateSerializer,
    PlatformEstateSerializer,
    PlatformEstateUpdateSerializer,
    PlatformOverviewSerializer,
)
from platform_admin.services import ADMIN_ROLE_CODES


def _estate_snapshot(estate: Estate) -> dict:
    return {
        "name": estate.name,
        "is_active": estate.is_active,
        "city": estate.city,
        "state": estate.state,
        "total_units": estate.total_units,
        "tier": estate.tier,
    }


class PlatformOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        from residents.models import ResidentProfile as RP

        data = {
            "estates_total": Estate.objects.count(),
            "estates_active": Estate.objects.filter(is_active=True).count(),
            "users_total": User.objects.filter(is_active=True).count(),
            "estate_admins_total": UserRole.objects.filter(
                is_active=True,
                role__code__in=ADMIN_ROLE_CODES,
            ).count(),
            "pending_registrations": RP.objects.filter(status=RP.Status.PENDING).count(),
            "units_total": Unit.objects.filter(is_active=True).count(),
        }
        return Response(PlatformOverviewSerializer(data).data)


class PlatformEstateViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    queryset = Estate.objects.all().order_by("-created_at")
    filterset_fields = ["is_active", "estate_type", "tier", "country", "city"]
    search_fields = ["name", "slug", "city"]
    ordering_fields = ["name", "created_at", "total_units"]

    def get_serializer_class(self):
        if self.action == "create":
            return PlatformEstateCreateSerializer
        if self.action in ("update", "partial_update"):
            return PlatformEstateUpdateSerializer
        return PlatformEstateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        estate = serializer.save()
        record_platform_audit(
            request=request,
            action=PlatformAuditLog.Action.ESTATE_CREATED,
            resource_type="estate",
            resource_id=estate.id,
            estate=estate,
            summary=f"Created estate {estate.name}",
            after_state=_estate_snapshot(estate),
        )
        output = PlatformEstateSerializer(estate, context=self.get_serializer_context())
        return Response(output.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        before_state = _estate_snapshot(instance)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance.refresh_from_db()
        after_state = _estate_snapshot(instance)

        if before_state["is_active"] and not after_state["is_active"]:
            action = PlatformAuditLog.Action.ESTATE_DEACTIVATED
            summary = f"Deactivated estate {instance.name}"
        elif not before_state["is_active"] and after_state["is_active"]:
            action = PlatformAuditLog.Action.ESTATE_ACTIVATED
            summary = f"Activated estate {instance.name}"
        else:
            action = PlatformAuditLog.Action.ESTATE_UPDATED
            summary = f"Updated estate {instance.name}"

        record_platform_audit(
            request=request,
            action=action,
            resource_type="estate",
            resource_id=instance.id,
            estate=instance,
            summary=summary,
            before_state=before_state,
            after_state=after_state,
        )
        return Response(PlatformEstateSerializer(instance).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        estate = self.get_object()
        if not estate.is_active:
            return Response({"detail": "Estate is already inactive."}, status=status.HTTP_400_BAD_REQUEST)

        before_state = _estate_snapshot(estate)
        estate.is_active = False
        estate.save(update_fields=["is_active", "updated_at"])
        after_state = _estate_snapshot(estate)
        record_platform_audit(
            request=request,
            action=PlatformAuditLog.Action.ESTATE_DEACTIVATED,
            resource_type="estate",
            resource_id=estate.id,
            estate=estate,
            summary=f"Deactivated estate {estate.name}",
            before_state=before_state,
            after_state=after_state,
        )
        return Response(PlatformEstateSerializer(estate).data)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        estate = self.get_object()
        if estate.is_active:
            return Response({"detail": "Estate is already active."}, status=status.HTTP_400_BAD_REQUEST)

        before_state = _estate_snapshot(estate)
        estate.is_active = True
        estate.save(update_fields=["is_active", "updated_at"])
        after_state = _estate_snapshot(estate)
        record_platform_audit(
            request=request,
            action=PlatformAuditLog.Action.ESTATE_ACTIVATED,
            resource_type="estate",
            resource_id=estate.id,
            estate=estate,
            summary=f"Activated estate {estate.name}",
            before_state=before_state,
            after_state=after_state,
        )
        return Response(PlatformEstateSerializer(estate).data)


class PlatformAdminViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = PlatformAdminSerializer
    filterset_fields = ["estate", "role__code", "is_active"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "estate__name"]

    def get_queryset(self):
        return (
            UserRole.objects.filter(
                is_active=True,
                role__code__in=ADMIN_ROLE_CODES,
            )
            .select_related("user", "role", "estate")
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return AssignPlatformAdminSerializer
        return PlatformAdminSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_role = serializer.save()
        record_platform_audit(
            request=request,
            action=PlatformAuditLog.Action.ADMIN_ASSIGNED,
            resource_type="user_role",
            resource_id=user_role.id,
            estate=user_role.estate,
            summary=(
                f"Assigned {user_role.role.name} to {user_role.user.email} "
                f"for {user_role.estate.name}"
            ),
            metadata={
                "user_email": user_role.user.email,
                "role_code": user_role.role.code,
                "estate_id": str(user_role.estate_id),
            },
        )
        output = PlatformAdminSerializer(user_role)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])
        record_platform_audit(
            request=self.request,
            action=PlatformAuditLog.Action.ADMIN_REVOKED,
            resource_type="user_role",
            resource_id=instance.id,
            estate=instance.estate,
            summary=(
                f"Revoked {instance.role.name} from {instance.user.email} "
                f"for {instance.estate.name}"
            ),
            metadata={
                "user_email": instance.user.email,
                "role_code": instance.role.code,
                "estate_id": str(instance.estate_id),
            },
        )


class PlatformAuditLogViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = PlatformAuditLogSerializer
    queryset = PlatformAuditLog.objects.select_related("actor", "estate").all()
    filterset_fields = ["action", "resource_type", "estate"]
    search_fields = ["summary", "actor__email", "estate__name"]
    ordering_fields = ["created_at", "action"]
