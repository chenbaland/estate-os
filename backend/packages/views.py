from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from core.viewsets import TenantViewSet
from packages.models import Package, PackageLog
from packages.serializers import PackageLogSerializer, PackageSerializer


class PackageViewSet(TenantViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    filterset_fields = ["recipient", "unit", "package_type", "status", "carrier"]
    search_fields = ["tracking_number", "sender_name", "description", "storage_location"]

    @action(detail=True, methods=["post"])
    def pickup(self, request, pk=None):
        package = self.get_object()
        previous_status = package.status
        package.status = Package.Status.COLLECTED
        package.collected_at = timezone.now()
        package.save(update_fields=["status", "collected_at", "updated_at"])

        PackageLog.objects.create(
            estate_id=package.estate_id,
            package=package,
            previous_status=previous_status,
            new_status=package.status,
            changed_by=request.user,
            notes=request.data.get("notes", ""),
            location=request.data.get("location", ""),
        )
        return Response(PackageSerializer(package).data)


class PackageLogViewSet(TenantViewSet):
    queryset = PackageLog.objects.all()
    serializer_class = PackageLogSerializer
    filterset_fields = ["package", "changed_by", "new_status"]
    search_fields = ["notes", "location"]
