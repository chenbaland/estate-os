from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserRole
from core.viewsets import TenantViewSet
from estates.models import Block, Estate, Unit
from estates.serializers import BlockSerializer, EstateSerializer, PublicEstateSerializer, PublicUnitSerializer, UnitSerializer


class PublicEstateListView(APIView):
    """List active estates available during self-registration."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        estates = Estate.objects.filter(is_deleted=False, is_active=True).order_by("name")
        serializer = PublicEstateSerializer(estates, many=True)
        return Response({"results": serializer.data})


class PublicEstateUnitsView(APIView):
    """List vacant units in an estate for self-registration."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, estate_id):
        try:
            estate = Estate.objects.get(id=estate_id, is_deleted=False, is_active=True)
        except Estate.DoesNotExist:
            return Response({"detail": "Estate not found."}, status=404)

        units = Unit.objects.filter(
            estate=estate,
            is_deleted=False,
            is_active=True,
            occupancy_status=Unit.OccupancyStatus.VACANT,
        ).order_by("unit_number")
        serializer = PublicUnitSerializer(units, many=True)
        return Response({"results": serializer.data})


class EstateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EstateSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["estate_type", "tier", "city", "country", "is_active"]
    search_fields = ["name", "slug", "city"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        qs = Estate.objects.filter(is_deleted=False)
        user = self.request.user
        if user.is_superuser:
            return qs
        estate_ids = UserRole.objects.filter(
            user=user,
            is_active=True,
        ).values_list("estate_id", flat=True)
        return qs.filter(id__in=estate_ids, is_active=True)


class BlockViewSet(TenantViewSet):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    filterset_fields = ["is_active", "code"]
    search_fields = ["name", "code"]


class UnitViewSet(TenantViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    filterset_fields = ["block", "unit_type", "occupancy_status", "is_active", "owner"]
    search_fields = ["unit_number"]
