from core.viewsets import TenantViewSet
from healthcare.models import AmbulanceRequest, Appointment, Hospital, MedicalRecord
from healthcare.serializers import (
    AmbulanceRequestSerializer,
    AppointmentSerializer,
    HospitalSerializer,
    MedicalRecordSerializer,
)


class HospitalViewSet(TenantViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    filterset_fields = ["is_partner", "is_active"]
    search_fields = ["name", "slug", "phone", "email"]


class AppointmentViewSet(TenantViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    filterset_fields = ["resident", "hospital", "status", "specialty"]
    search_fields = ["doctor_name", "reason", "notes"]


class AmbulanceRequestViewSet(TenantViewSet):
    queryset = AmbulanceRequest.objects.all()
    serializer_class = AmbulanceRequestSerializer
    filterset_fields = ["resident", "status", "priority", "destination_hospital"]
    search_fields = ["pickup_location", "patient_condition"]


class MedicalRecordViewSet(TenantViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    filterset_fields = ["resident", "hospital", "record_type", "is_confidential"]
    search_fields = ["title", "description", "provider_name"]
