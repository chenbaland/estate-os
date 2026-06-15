from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.viewsets import TenantReadOnlyViewSet, TenantViewSet
from visitors.models import Blacklist, VisitorLog, VisitorPass
from visitors.serializers import (
    BlacklistSerializer,
    VisitorLogSerializer,
    VisitorPassScanSerializer,
    VisitorPassSerializer,
)


class VisitorPassViewSet(TenantViewSet):
    queryset = VisitorPass.objects.select_related("host")
    serializer_class = VisitorPassSerializer
    filterset_fields = ["host", "pass_type", "status"]
    search_fields = ["visitor_name", "visitor_phone", "visitor_email", "qr_code", "vehicle_plate"]

    @action(detail=False, methods=["post"])
    def scan(self, request):
        serializer = VisitorPassScanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qr_code = serializer.validated_data["qr_code"]
        gate_name = serializer.validated_data.get("gate_name", "")
        direction = serializer.validated_data["direction"]
        estate_id = getattr(request, "estate_id", None)

        try:
            visitor_pass = self.get_queryset().get(qr_code=qr_code)
        except VisitorPass.DoesNotExist:
            return Response(
                {"valid": False, "detail": "Invalid QR code."},
                status=status.HTTP_404_NOT_FOUND,
            )

        now = timezone.now()
        if visitor_pass.status != VisitorPass.Status.ACTIVE:
            return Response(
                {"valid": False, "detail": "Pass is not active.", "status": visitor_pass.status},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if visitor_pass.valid_until < now:
            visitor_pass.status = VisitorPass.Status.EXPIRED
            visitor_pass.save(update_fields=["status", "updated_at"])
            return Response(
                {"valid": False, "detail": "Pass has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        blacklist_q = Q(is_active=True)
        name_or_phone_q = Q()
        if visitor_pass.visitor_phone:
            name_or_phone_q |= Q(phone=visitor_pass.visitor_phone)
        if visitor_pass.visitor_name:
            name_or_phone_q |= Q(full_name__iexact=visitor_pass.visitor_name)
        if name_or_phone_q:
            blacklist_q &= name_or_phone_q
        if estate_id and name_or_phone_q and Blacklist.objects.filter(estate_id=estate_id).filter(blacklist_q).exists():
            return Response(
                {"valid": False, "detail": "Visitor is blacklisted."},
                status=status.HTTP_403_FORBIDDEN,
            )

        log = VisitorLog.objects.create(
            estate_id=visitor_pass.estate_id,
            visitor_pass=visitor_pass,
            visitor_name=visitor_pass.visitor_name,
            visitor_phone=visitor_pass.visitor_phone,
            host=visitor_pass.host,
            direction=direction,
            verification_method=VisitorLog.VerificationMethod.QR,
            gate_name=gate_name,
            vehicle_plate=visitor_pass.vehicle_plate,
            verified_by=request.user if request.user.is_authenticated else None,
        )

        visitor_pass.entries_used += 1
        if visitor_pass.entries_used >= visitor_pass.max_entries:
            visitor_pass.status = VisitorPass.Status.USED
        visitor_pass.save(update_fields=["entries_used", "status", "updated_at"])

        return Response(
            {
                "valid": True,
                "visitor_pass": VisitorPassSerializer(visitor_pass).data,
                "log_id": str(log.id),
            }
        )


class VisitorLogViewSet(TenantReadOnlyViewSet):
    queryset = VisitorLog.objects.select_related("visitor_pass", "host", "verified_by")
    serializer_class = VisitorLogSerializer
    filterset_fields = ["visitor_pass", "host", "direction", "verification_method", "gate_name"]
    search_fields = ["visitor_name", "visitor_phone", "gate_name"]


class BlacklistViewSet(TenantViewSet):
    queryset = Blacklist.objects.all()
    serializer_class = BlacklistSerializer
    filterset_fields = ["reason", "is_active"]
    search_fields = ["full_name", "phone", "email", "license_plate", "id_document_number"]
